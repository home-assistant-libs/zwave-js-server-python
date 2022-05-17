"""Provide a model for the Z-Wave JS node's statistics."""
from typing import TYPE_CHECKING, Optional

from zwave_js_server.exceptions import RssiErrorReceived

from ...const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED, RssiError
from ..statistics import RouteStatistics, RouteStatisticsDataType

if TYPE_CHECKING:
    from ...client import Client

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class NodeStatisticsDataType(TypedDict, total=False):
    """Represent a node statistics data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/NodeStatistics.ts#L21-L33
    commandsTX: int
    commandsRX: int
    commandsDroppedTX: int
    commandsDroppedRX: int
    timeoutResponse: int
    rtt: int
    rssi: int
    lwr: RouteStatisticsDataType
    nlwr: RouteStatisticsDataType


class NodeStatistics:
    """Represent a node statistics update."""

    def __init__(
        self, client: "Client", data: Optional[NodeStatisticsDataType]
    ) -> None:
        """Initialize node statistics."""
        self.data = data or NodeStatisticsDataType(
            commandsDroppedRX=0,
            commandsDroppedTX=0,
            commandsRX=0,
            commandsTX=0,
            timeoutResponse=0,
        )
        self.client = client
        self._lwr = None
        if lwr := self.data.get("lwr"):
            self._lwr = RouteStatistics(client, lwr)
        self._nlwr = None
        if nlwr := self.data.get("nlwr"):
            self._nlwr = RouteStatistics(client, nlwr)

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

    @property
    def rtt(self) -> Optional[int]:
        """
        Return average round trip time (RTT) to this node in milliseconds.

        Consecutive measurements are combined using an exponential moving average.
        """
        return self.data.get("rtt")

    @property
    def rssi(self) -> Optional[int]:
        """
        Return average RSSI of frames received by this node.

        Consecutive non-error measurements are combined using an exponential moving
        average.
        """
        if (rssi_ := self.data.get("rssi")) is None:
            return None
        if rssi_ in [item.value for item in RssiError]:
            raise RssiErrorReceived(RssiError(rssi_))
        return rssi_

    @property
    def lwr(self) -> Optional[RouteStatistics]:
        """Return last working route from the controller to this node."""
        return self._lwr

    @property
    def nlwr(self) -> Optional[RouteStatistics]:
        """Return next to last working route from the controller to this node."""
        return self._nlwr
