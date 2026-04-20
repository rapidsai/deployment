"""Register all flows with Prefect work pools and schedules."""

from prefect import serve

from pipeline.flows.deploy import deploy_flow
from pipeline.flows.evaluate import evaluate_flow
from pipeline.flows.full_pipeline import full_pipeline_flow
from pipeline.flows.preprocess import preprocess_flow
from pipeline.flows.train import train_flow


def main():
    """Register and serve all deployments."""
    preprocess_deploy = preprocess_flow.to_deployment(
        name="preprocess",
        work_pool_name="gpu",
        cron="0 0 * * *",
    )
    train_deploy = train_flow.to_deployment(
        name="train",
        work_pool_name="gpu",
    )
    evaluate_deploy = evaluate_flow.to_deployment(
        name="evaluate",
        work_pool_name="gpu",
    )
    deploy_deploy = deploy_flow.to_deployment(
        name="deploy",
        work_pool_name="gpu",
    )
    full_pipeline_deploy = full_pipeline_flow.to_deployment(
        name="full-pipeline",
        work_pool_name="gpu",
        cron="0 2 * * *",
    )

    serve(
        preprocess_deploy,
        train_deploy,
        evaluate_deploy,
        deploy_deploy,
        full_pipeline_deploy,
    )


if __name__ == "__main__":
    main()
