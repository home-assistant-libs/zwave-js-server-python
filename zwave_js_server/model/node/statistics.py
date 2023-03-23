"""Provide a model for the Z-Wave JS node's statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from zwave_js_server.exceptions import RssiErrorReceived

from ...const import RssiError
from ..statistics import RouteStatistics, RouteStatisticsDataType

if TYPE_CHECKING:
    from ...client import Client


class NodeStatisticsDataType(TypedDict, total=False):
    """Represent a node statistics data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/node/NodeStatistics.ts#L21-L33
    commandsTX: int  # required
    commandsRX: int  # required
    commandsDroppedTX: int  # required
    commandsDroppedRX: int  # required
    timeoutResponse: int  # required
    rtt: int
    rssi: int
    lwr: RouteStatisticsDataType
    nlwr: RouteStatisticsDataType


@dataclass
class NodeStatistics:
    """Represent a node statistics update."""

    client: "Client"
    data: NodeStatisticsDataType | None = None
    commands_tx: int = field(init=False)
    commands_rx: int = field(init=False)
    commands_dropped_rx: int = field(init=False)
    commands_dropped_tx: int = field(init=False)
    timeout_response: int = field(init=False)
    rtt: int | None = field(init=False)
    lwr: RouteStatistics | None = field(init=False, default=None)
    nlwr: RouteStatistics | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post initialize."""
        data = self.data or NodeStatisticsDataType(
            commandsDroppedRX=0,
            commandsDroppedTX=0,
            commandsRX=0,
            commandsTX=0,
            timeoutResponse=0,
        )
        self.commands_tx = data["commandsTX"]
        self.commands_rx = data["commandsRX"]
        self.commands_dropped_rx = data["commandsDroppedRX"]
        self.commands_dropped_tx = data["commandsDroppedTX"]
        self.timeout_response = data["timeoutResponse"]
        self.rtt = data.get("rtt")
        if lwr := data.get("lwr"):
            self.lwr = RouteStatistics(self.client, lwr)
        if nlwr := data.get("nlwr"):
            self.nlwr = RouteStatistics(self.client, nlwr)

    @property
    def rssi(self) -> int | None:
        """
        Return average RSSI of frames received by this node.

        Consecutive non-error measurements are combined using an exponential moving
        average.
        """
        if not self.data or (rssi_ := self.data.get("rssi")) is None:
            return None
        if rssi_ in [item.value for item in RssiError]:
            raise RssiErrorReceived(RssiError(rssi_))
        return rssi_
