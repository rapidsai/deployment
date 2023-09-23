import argparse
import glob
import os
import time
from functools import partial

import dask
import optuna
import pandas as pd
import xgboost as xgb
from dask.distributed import Client, LocalCluster, wait
from dask_cuda import LocalCUDACluster
from optuna.samplers import RandomSampler
from sklearn.ensemble import RandomForestClassifier as RF_cpu
from sklearn.metrics import accuracy_score as accuracy_score_cpu
from sklearn.model_selection import train_test_split

n_cv_folds = 5

label_column = "ArrDel15"
feature_columns = [
    "Year",
    "Quarter",
    "Month",
    "DayOfWeek",
    "Flight_Number_Reporting_Airline",
    "DOT_ID_Reporting_Airline",
    "OriginCityMarketID",
    "DestCityMarketID",
    "DepTime",
    "DepDelay",
    "DepDel15",
    "ArrDel15",
    "AirTime",
    "Distance",
]


def ingest_data(target):
    if target == "gpu":
        import cudf

        dataset = cudf.read_parquet(
            glob.glob("./data/*.parquet"),
            columns=feature_columns,
        )
    else:
        dataset = pd.read_parquet(
            glob.glob("./data/*.parquet"),
            columns=feature_columns,
        )
    return dataset


def preprocess_data(dataset, *, i_fold):
    dataset = dataset.dropna()
    train, test = train_test_split(dataset, random_state=i_fold, shuffle=True)
    X_train, y_train = train.drop(label_column, axis=1), train[label_column]
    X_test, y_test = test.drop(label_column, axis=1), test[label_column]
    X_train, y_train = X_train.astype("float32"), y_train.astype("int32")
    X_test, y_test = X_test.astype("float32"), y_test.astype("int32")

    return X_train, y_train, X_test, y_test


def train_xgboost(trial, *, target, dataset=None, threads_per_worker=None):
    if target == "gpu":
        dataset = ingest_data(target)

    params = {
        "max_depth": trial.suggest_int("max_depth", 4, 8),
        "learning_rate": trial.suggest_float("learning_rate", 0.001, 0.1, log=True),
        "min_child_weight": trial.suggest_float(
            "min_child_weight", 0.1, 10.0, log=True
        ),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.0001, 100, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.0001, 100, log=True),
        "verbosity": 0,
        "objective": "binary:logistic",
    }
    num_boost_round = trial.suggest_int("num_boost_round", 100, 500, step=10)

    cv_fold_scores = []
    for i_fold in range(n_cv_folds):
        X_train, y_train, X_test, y_test = preprocess_data(dataset, i_fold=i_fold)
        dtrain = xgb.QuantileDMatrix(X_train, label=y_train)
        dtest = xgb.QuantileDMatrix(X_test)

        if target == "gpu":
            from cuml.metrics import accuracy_score as accuracy_score_gpu

            params["tree_method"] = "gpu_hist"
            accuracy_score_func = accuracy_score_gpu
        else:
            params["tree_method"] = "hist"
            params["nthread"] = threads_per_worker
            accuracy_score_func = accuracy_score_cpu

        trained_model = xgb.train(params, dtrain, num_boost_round=num_boost_round)

        pred = trained_model.predict(dtest) > 0.5
        pred = pred.astype("int32")
        score = accuracy_score_func(y_test, pred)
        cv_fold_scores.append(score)
    final_score = sum(cv_fold_scores) / len(cv_fold_scores)
    return final_score


def train_randomforest(trial, *, target, dataset=None, threads_per_worker=None):
    if target == "gpu":
        dataset = ingest_data(target)

    params = {
        "max_depth": trial.suggest_int("max_depth", 5, 15),
        "max_features": trial.suggest_float("max_features", 0.1, 1.0),
        "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=10),
        "criterion": trial.suggest_categorical("criterion", ["gini", "entropy"]),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 1000, log=True),
    }

    cv_fold_scores = []
    for i_fold in range(n_cv_folds):
        X_train, y_train, X_test, y_test = preprocess_data(dataset)

        if target == "gpu":
            from cuml.ensemble import RandomForestClassifier as RF_gpu
            from cuml.metrics import accuracy_score as accuracy_score_gpu

            params["n_bins"] = 256
            trained_model = RF_gpu(**params)
            accuracy_score_func = accuracy_score_gpu
        else:
            params["n_jobs"] = threads_per_worker
            trained_model = RF_cpu(**params)
            accuracy_score_func = accuracy_score_cpu

        trained_model.fit(X_train, y_train)
        pred = trained_model.predict(X_test)
        score = accuracy_score_func(y_test, pred)
        cv_fold_scores.append(score)
    final_score = sum(cv_fold_scores) / len(cv_fold_scores)
    return final_score


def main(args):
    tstart = time.perf_counter()

    if args.target == "gpu":
        cluster = LocalCUDACluster()
    else:
        cluster = LocalCluster(
            n_workers=os.cpu_count() // args.threads_per_worker,
            threads_per_worker=args.threads_per_worker,
        )
    n_workers = len(cluster.workers)
    n_trials = 8

    dataset = None
    # For CPU target, load the data matrix once and shared it among workers
    # For GPU target, each worker process will get its own data matrix
    if args.target == "cpu":
        dataset = ingest_data("cpu")

    futures = []
    if args.model_type == "XGBoost":
        if args.target == "gpu":
            objective_func = partial(train_xgboost, target=args.target)
        else:
            objective_func = partial(
                train_xgboost,
                target=args.target,
                dataset=dataset,
                threads_per_worker=args.threads_per_worker,
            )
    else:
        if args.target == "gpu":
            objective_func = partial(train_randomforest, target=args.target)
        else:
            objective_func = partial(
                train_randomforest,
                target=args.target,
                dataset=dataset,
                threads_per_worker=args.threads_per_worker,
            )
    with Client(cluster) as client:
        backend_storage = optuna.storages.InMemoryStorage()
        dask_storage = optuna.integration.DaskStorage(
            storage=backend_storage, client=client
        )

        study = optuna.create_study(
            direction="maximize",
            sampler=optuna.samplers.RandomSampler(seed=args.seed),
            storage=dask_storage,
        )
        for i in range(0, n_trials, n_workers):
            iter_range = (i, min([i + n_workers, n_trials]))
            futures.append(
                {
                    "range": iter_range,
                    "futures": [
                        client.submit(
                            study.optimize, objective_func, n_trials=1, pure=False
                        )
                        for _ in range(*iter_range)
                    ],
                }
            )
        for partition in futures:
            iter_range = partition["range"]
            print(
                f"Testing hyperparameter combinations {iter_range[0]}..{iter_range[1]}"
            )
            _ = wait(partition["futures"])
            for fut in partition["futures"]:
                _ = fut.result()  # Ensure that the training job was successful
            tnow = time.perf_counter()
            print(
                f"Best cross-validation metric: {study.best_value}, Time elapsed = {tnow - tstart}"
            )
    tend = time.perf_counter()
    print(f"Time elapsed: {tend - tstart} sec")
    cluster.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-type", type=str, required=True, choices=["XGBoost", "RandomForest"]
    )
    parser.add_argument("--target", required=True, choices=["gpu", "cpu"])
    parser.add_argument("--seed", required=False, type=int, default=1)
    parser.add_argument(
        "--threads_per_worker",
        required=False,
        type=int,
        default=4,
        help="Number of threads per worker process. Only applicable for CPU target",
    )
    args = parser.parse_args()
    main(args)
