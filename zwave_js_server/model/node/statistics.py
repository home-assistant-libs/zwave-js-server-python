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
    commandsTX: int
    commandsRX: int
    commandsDroppedTX: int
    commandsDroppedRX: int
    timeoutResponse: int
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
    lwr: RouteStatistics | None = field(init=False)
    nlwr: RouteStatistics | None = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.data = self.data or NodeStatisticsDataType(
            commandsDroppedRX=0,
            commandsDroppedTX=0,
            commandsRX=0,
            commandsTX=0,
            timeoutResponse=0,
        )
        self.commands_tx = self.data["commandsTX"]
        self.commands_rx = self.data["commandsRX"]
        self.commands_dropped_rx = self.data["commandsDroppedRX"]
        self.commands_dropped_tx = self.data["commandsDroppedTX"]
        self.timeout_response = self.data["timeoutResponse"]
        self.rtt = self.data.get("rtt")
        self.lwr = (
            RouteStatistics(self.client, self.data["lwr"])
            if "lwr" in self.data
            else None
        )
        self.nlwr = (
            RouteStatistics(self.client, self.data["nlwr"])
            if "nlwr" in self.data
            else None
        )
        self._lwr = None
        if lwr := self.data.get("lwr"):
            self._lwr = RouteStatistics(self.client, lwr)
        self._nlwr = None
        if nlwr := self.data.get("nlwr"):
            self._nlwr = RouteStatistics(self.client, nlwr)

    @property
    def rssi(self) -> int | None:
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
