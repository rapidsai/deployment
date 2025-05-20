#!/usr/bin/env python3

import logging
import os
from pprint import pprint

from message_filter_stage import MessageFilterStage
from morpheus.common import FilterSource
from morpheus.config import Config, PipelineModes
from morpheus.pipeline import LinearPipeline
from morpheus.stages.general.monitor_stage import MonitorStage
from morpheus.stages.inference.triton_inference_stage import TritonInferenceStage
from morpheus.stages.input.kafka_source_stage import KafkaSourceStage
from morpheus.stages.output.write_to_kafka_stage import WriteToKafkaStage
from morpheus.stages.postprocess.add_classifications_stage import (
    AddClassificationsStage,
)
from morpheus.stages.postprocess.filter_detections_stage import FilterDetectionsStage
from morpheus.stages.postprocess.serialize_stage import SerializeStage
from morpheus.stages.preprocess.deserialize_stage import DeserializeStage
from morpheus.stages.preprocess.preprocess_nlp_stage import PreprocessNLPStage
from morpheus.utils.file_utils import get_data_file_path, load_labels_file
from morpheus.utils.logger import configure_logging
from network_traffic_analyzer_stage import NetworkTrafficAnalyzerStage


def main():
    # Get the Kafka bootstrap server from the environment variable
    bootstrap_server = os.getenv("KAFKA_CLUSTER_BOOTSTRAP_SERVER")
    if not bootstrap_server:
        raise RuntimeError(
            """KAFKA_CLUSTER_BOOTSTRAP_SERVER environment variable 
        is not set. Please set it to your Kafka bootstrap service address."""
        )

    # Get the Triton server URL from the environment variable
    triton_server = os.getenv("TRITON_SERVER")
    if not triton_server:
        raise RuntimeError(
            """TRITON_SERVER environment variable 
        is not set. Please set it to your Triton Inference Server address."""
        )

    # Configure logging
    configure_logging(log_level=logging.DEBUG)

    # Create a pipeline configuration
    config = Config()
    config.mode = PipelineModes.NLP
    config.pipeline_batch_size = 1024
    config.model_max_batch_size = 32
    config.feature_length = 256
    config.num_threads = min(
        len(os.sched_getaffinity(0)), 16
    )  # choose threads = num cores unless more than 16
    config.class_labels = load_labels_file(get_data_file_path("data/labels_nlp.txt"))

    # Print the config dictionary
    pprint(vars(config))

    # Confirm we are using right kafka bootstrap server
    print(f"Using Kafka bootstrap server: {bootstrap_server}")

    # Create the pipeline
    pipeline = LinearPipeline(config)

    # Add stages to the pipeline
    pipeline.set_source(
        KafkaSourceStage(
            config,
            bootstrap_servers=bootstrap_server,
            input_topic=["network-traffic-input"],
            group_id="network-traffic-group",
            auto_offset_reset="earliest",
        )
    )
    pipeline.add_stage(DeserializeStage(config))
    pipeline.add_stage(MessageFilterStage(config, column="data", min_length=50))
    pipeline.add_stage(
        PreprocessNLPStage(
            config,
            vocab_hash_file="data/bert-base-uncased-hash.txt",
            do_lower_case=True,
            truncation=True,
            add_special_tokens=False,
        )
    )
    pipeline.add_stage(
        TritonInferenceStage(
            config,
            model_name="sid-minibert-onnx",
            server_url=triton_server,
            force_convert_inputs=True,
        )
    )
    pipeline.add_stage(
        MonitorStage(config, description="Inference Rate", smoothing=0.001, unit="inf")
    )
    pipeline.add_stage(AddClassificationsStage(config))
    pipeline.add_stage(FilterDetectionsStage(config, filter_source=FilterSource.TENSOR))
    pipeline.add_stage(NetworkTrafficAnalyzerStage(config))
    pipeline.add_stage(SerializeStage(config, exclude=["^_ts_"]))

    # Add Kafka sink stage
    pipeline.add_stage(
        WriteToKafkaStage(
            config,
            bootstrap_servers=bootstrap_server,
            output_topic="network-traffic-results",
        )
    )

    # Run the pipeline
    pipeline.run()


if __name__ == "__main__":
    main()
