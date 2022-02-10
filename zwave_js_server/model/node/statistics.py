"""Provide a model for the Z-Wave JS node's statistics."""
from typing import Optional, TypedDict


class NodeStatisticsDataType(TypedDict):
    """Represent a node statistics data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/NodeStatistics.ts#L21-L33
    commandsTX: int
    commandsRX: int
    commandsDroppedTX: int
    commandsDroppedRX: int
    timeoutResponse: int


class NodeStatistics:
    """Represent a node statistics update."""

    def __init__(self, data: Optional[NodeStatisticsDataType] = None) -> None:
        """Initialize node statistics."""
        self.data = data or NodeStatisticsDataType(
            commandsDroppedRX=0,
            commandsDroppedTX=0,
            commandsRX=0,
            commandsTX=0,
            timeoutResponse=0,
        )

    @property
    def commands_tx(self) -> int:
        """Return number of commands successfully sent to node."""
        return self.data["commandsTX"]

    @property
    def commands_rx(self) -> int:
        """
        Return number of commands received from node.

        Includes responses to sent commands.
        """
        return self.data["commandsRX"]

    @property
    def commands_dropped_rx(self) -> int:
        """Return number of commands from node that were dropped by host."""
        return self.data["commandsDroppedRX"]

    @property
    def commands_dropped_tx(self) -> int:
        """
        Return number of outgoing commands that were dropped.

        These commands could not be sent.
        """
        return self.data["commandsDroppedTX"]

    @property
    def timeout_response(self) -> int:
        """Return number of Get-type cmds where node's response didn't come in time."""
        return self.data["timeoutResponse"]
