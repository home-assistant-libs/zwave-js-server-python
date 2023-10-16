"""Provide a model for the Z-Wave JS node's statistics."""
from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime
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
    lastSeen: str


@dataclass
class NodeStatistics:
    """Represent a node statistics update."""

    client: Client = field(repr=False)
    data: NodeStatisticsDataType = field(repr=False)
    commands_tx: int = field(init=False)
    commands_rx: int = field(init=False)
    commands_dropped_rx: int = field(init=False)
    commands_dropped_tx: int = field(init=False)
    timeout_response: int = field(init=False)
    rtt: int | None = field(init=False)
    lwr: RouteStatistics | None = field(init=False, default=None)
    nlwr: RouteStatistics | None = field(init=False, default=None)
    last_seen: datetime | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.commands_tx = self.data["commandsTX"]
        self.commands_rx = self.data["commandsRX"]
        self.commands_dropped_rx = self.data["commandsDroppedRX"]
        self.commands_dropped_tx = self.data["commandsDroppedTX"]
        self.timeout_response = self.data["timeoutResponse"]
        self.rtt = self.data.get("rtt")
        if last_seen := self.data.get("lastSeen"):
            self.last_seen = datetime.fromisoformat(last_seen)
        if lwr := self.data.get("lwr"):
            with suppress(ValueError):
                self.lwr = RouteStatistics(self.client, lwr)
        if nlwr := self.data.get("nlwr"):
            with suppress(ValueError):
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
