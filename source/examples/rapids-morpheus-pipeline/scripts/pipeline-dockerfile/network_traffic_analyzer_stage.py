import cudf
import mrc
from morpheus.messages import ControlMessage, MessageMeta
from morpheus.pipeline.single_port_stage import SinglePortStage
from morpheus.pipeline.stage_schema import StageSchema
from mrc.core import operators as ops


class NetworkTrafficAnalyzerStage(SinglePortStage):
    """
    A stage that analyzes network traffic patterns using GPU-accelerated operations.
    This stage adds insights about high-volume sources/destinations and common port pairs.
    """

    def __init__(self, c):
        super().__init__(c)

    @property
    def name(self) -> str:
        return "network-traffic-analyzer"

    def accepted_types(self) -> tuple:
        return (ControlMessage,)

    def supports_cpp_node(self) -> bool:
        return False

    def compute_schema(self, schema: StageSchema):
        schema.output_schema.set_type(ControlMessage)

    def on_data(self, message: ControlMessage) -> ControlMessage:
        if message is None:
            return None

        with message.payload().mutable_dataframe() as df:
            # Convert to cuDF DataFrame for GPU-accelerated operations
            cudf_df = cudf.DataFrame(df)

            # Convert data_len to numeric type
            cudf_df["data_len"] = cudf_df["data_len"].astype("int64")

            # 1. Identify high-volume source IPs
            src_ip_stats = cudf_df.groupby("src_ip")["data_len"].sum().reset_index()
            high_volume_src_ips = src_ip_stats[
                src_ip_stats["data_len"] > src_ip_stats["data_len"].mean()
            ]["src_ip"]
            cudf_df["is_high_volume_src"] = cudf_df["src_ip"].isin(high_volume_src_ips)

            # 2. Identify high-volume destination IPs
            dest_ip_stats = cudf_df.groupby("dest_ip")["data_len"].sum().reset_index()
            high_volume_dest_ips = dest_ip_stats[
                dest_ip_stats["data_len"] > dest_ip_stats["data_len"].mean()
            ]["dest_ip"]
            cudf_df["is_high_volume_dest"] = cudf_df["dest_ip"].isin(
                high_volume_dest_ips
            )

            # 3. Identify common port pairs
            # Create port pair identifiers using string concatenation
            cudf_df["port_pair"] = cudf_df["src_port"] + ":" + cudf_df["dest_port"]

            # Count occurrences of each port pair
            port_stats = cudf_df["port_pair"].value_counts().reset_index()
            port_stats.columns = ["port_pair", "count"]

            # Identify common port pairs (above average frequency)
            common_port_pairs = port_stats[
                port_stats["count"] > port_stats["count"].mean()
            ]["port_pair"]

            # Check if each port pair is common
            cudf_df["is_common_port_pair"] = cudf_df["port_pair"].isin(
                common_port_pairs
            )

            # Remove temporary column
            cudf_df = cudf_df.drop("port_pair", axis=1)

            # Create new metadata with the analysis results
            new_meta = MessageMeta(cudf_df)
            message.payload(new_meta)

        return message

    def _build_single(
        self, builder: mrc.Builder, input_node: mrc.SegmentObject
    ) -> mrc.SegmentObject:
        node = builder.make_node(self.unique_name, ops.map(self.on_data))
        builder.make_edge(input_node, node)
        return node
