import mrc
from morpheus.messages import ControlMessage, MessageMeta
from morpheus.pipeline.single_port_stage import SinglePortStage
from morpheus.pipeline.stage_schema import StageSchema
from mrc.core import operators as ops


class MessageFilterStage(SinglePortStage):
    """
    A stage that filters out messages shorter than a specified length using GPU-accelerated operations.

    Parameters
    ----------
    column : str, default = 'data'
        The column containing the text to filter
    min_length : int, default = 10
        Minimum length of messages to keep. Messages shorter than this will be filtered out.
    """

    def __init__(self, c, column: str = "data", min_length: int = 50):
        super().__init__(c)
        self._column = column
        self._min_length = min_length

    @property
    def name(self) -> str:
        return "message-filter"

    def accepted_types(self) -> tuple:
        return (ControlMessage,)

    def supports_cpp_node(self) -> bool:
        return False

    def compute_schema(self, schema: StageSchema):
        schema.output_schema.set_type(ControlMessage)

    def on_data(self, message: ControlMessage) -> ControlMessage:
        # Get the payload from the ControlMessage
        if message is None:
            return None

        with message.payload().mutable_dataframe() as cudf_df:
            # Filter based on column length
            mask = cudf_df[self._column].str.len() >= self._min_length

            new_meta = MessageMeta(cudf_df[mask])

            # Set the new metadata as the payload
            message.payload(new_meta)

        return message

    def _build_single(
        self, builder: mrc.Builder, input_node: mrc.SegmentObject
    ) -> mrc.SegmentObject:
        node = builder.make_node(self.unique_name, ops.map(self.on_data))
        builder.make_edge(input_node, node)
        return node
