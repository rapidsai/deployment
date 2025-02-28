#
# Copyright (c) 2019-2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import os

import cudf
import cuml
import mlflow
from rapids_csp_azure import PerfTimer, RapidsCloudML


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--data_dir", type=str, help="location of data")
    parser.add_argument(
        "--n_estimators", type=int, default=100, help="Number of trees in RF"
    )
    parser.add_argument(
        "--max_depth", type=int, default=16, help="Max depth of each tree"
    )
    parser.add_argument(
        "--n_bins",
        type=int,
        default=8,
        help="Number of bins used in split point calculation",
    )
    parser.add_argument(
        "--max_features",
        type=float,
        default=1.0,
        help="Number of features for best split",
    )
    parser.add_argument(
        "--compute",
        type=str,
        default="single-GPU",
        help="set to multi-GPU for algorithms via dask",
    )
    parser.add_argument(
        "--cv_folds", type=int, default=5, help="Number of CV fold splits"
    )

    args = parser.parse_args()
    data_dir = args.data_dir
    compute = args.compute
    cv_folds = args.cv_folds

    n_estimators = args.n_estimators
    mlflow.log_param("n_estimators", int(args.n_estimators))
    max_depth = args.max_depth
    mlflow.log_param("max_depth", int(args.max_depth))
    n_bins = args.n_bins
    mlflow.log_param("n_bins", int(args.n_bins))
    max_features = args.max_features
    mlflow.log_param("max_features", str(args.max_features))

    print("\n---->>>> cuDF version <<<<----\n", cudf.__version__)
    print("\n---->>>> cuML version <<<<----\n", cuml.__version__)

    azure_ml = RapidsCloudML(
        cloud_type="Azure",
        model_type="RandomForest",
        data_type="Parquet",
        compute_type=compute,
    )
    print(args.compute)

    if compute == "single-GPU":
        dataset, _, y_label, _ = azure_ml.load_data(filename=data_dir)
    else:
        # use parquet files from 'https://airlinedataset.blob.core.windows.net/airline-10years' for multi-GPU training
        dataset, _, y_label, _ = azure_ml.load_data(
            filename=os.path.join(data_dir, "part*.parquet"),
            col_labels=[
                "Flight_Number_Reporting_Airline",
                "Year",
                "Quarter",
                "Month",
                "DayOfWeek",
                "DOT_ID_Reporting_Airline",
                "OriginCityMarketID",
                "DestCityMarketID",
                "DepTime",
                "DepDelay",
                "DepDel15",
                "ArrDel15",
                "ArrDelay",
                "AirTime",
                "Distance",
            ],
            y_label="ArrDel15",
        )

    X = dataset[dataset.columns.difference(["ArrDelay", y_label])]
    y = dataset[y_label]
    del dataset

    print("\n---->>>> Training using GPUs <<<<----\n")

    # ----------------------------------------------------------------------------------------------------
    # cross-validation folds
    # ----------------------------------------------------------------------------------------------------
    accuracy_per_fold = []
    train_time_per_fold = []
    infer_time_per_fold = []
    trained_model = []
    global_best_test_accuracy = 0

    model_params = {
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "max_features": max_features,
        "n_bins": n_bins,
    }

    # optional cross-validation w/ model_params['n_train_folds'] > 1
    for i_train_fold in range(cv_folds):
        print(f"\n CV fold { i_train_fold } of { cv_folds }\n")

        # split data
        X_train, X_test, y_train, y_test, _ = azure_ml.split_data(
            X, y, random_state=i_train_fold
        )
        # train model
        trained_model, training_time = azure_ml.train_model(
            X_train, y_train, model_params
        )

        train_time_per_fold.append(round(training_time, 4))

        # evaluate perf
        test_accuracy, infer_time = azure_ml.evaluate_test_perf(
            trained_model, X_test, y_test
        )
        accuracy_per_fold.append(round(test_accuracy, 4))
        infer_time_per_fold.append(round(infer_time, 4))

        # update best model [ assumes maximization of perf metric ]
        if test_accuracy > global_best_test_accuracy:
            global_best_test_accuracy = test_accuracy

    mlflow.log_metric(
        "Total training inference time", float(training_time + infer_time)
    )
    mlflow.log_metric("Accuracy", float(global_best_test_accuracy))
    print("\n Accuracy             :", global_best_test_accuracy)
    print("\n accuracy per fold    :", accuracy_per_fold)
    print("\n train-time per fold  :", train_time_per_fold)
    print("\n train-time all folds :", sum(train_time_per_fold))
    print("\n infer-time per fold  :", infer_time_per_fold)
    print("\n infer-time all folds :", sum(infer_time_per_fold))


if __name__ == "__main__":
    with PerfTimer() as total_script_time:
        main()
    print(f"Total runtime: {total_script_time.duration:.2f}")
    mlflow.log_metric("Total runtime", float(total_script_time.duration))
    print("\n Exiting script")
