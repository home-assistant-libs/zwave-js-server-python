"""Common models for statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from zwave_js_server.exceptions import RepeaterRssiErrorReceived, RssiErrorReceived

from ..const import ProtocolDataRate, RssiError

if TYPE_CHECKING:
    from ..client import Client
    from .node import Node


class RouteStatisticsDataType(TypedDict, total=False):
    """Represent a route statistics data dict type."""

    protocolDataRate: int
    repeaters: list[int]
    rssi: int
    repeaterRSSI: list[int]
    routeFailedBetween: list[int]


class RouteStatisticsDict(TypedDict):
    """Represent a route statistics data dict type."""

    protocol_data_rate: int
    repeaters: list["Node"]
    rssi: int | None
    repeater_rssi: list[int]
    route_failed_between: tuple["Node", "Node"] | None


@dataclass
class RouteStatistics:
    """Represent route statistics."""

    client: "Client"
    data: RouteStatisticsDataType
    protocol_data_rate: ProtocolDataRate = field(init=False)
    repeaters: list["Node"] = field(init=False)
    route_failed_between: tuple["Node", "Node"] | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.protocol_data_rate = ProtocolDataRate(self.data["protocolDataRate"])
        assert self.client.driver
        self.repeaters = [
            self.client.driver.controller.nodes[node_id]
            for node_id in self.data["repeaters"]
        ]
        if node_ids := self.data.get("routeFailedBetween"):
            assert len(node_ids) == 2
            self.route_failed_between = (
                self.client.driver.controller.nodes[node_ids[0]],
                self.client.driver.controller.nodes[node_ids[1]],
            )

    @property
    def rssi(self) -> int | None:
        """Return RSSI."""
        if (rssi := self.data.get("rssi")) is None:
            return None
        if rssi in [item.value for item in RssiError]:
            raise RssiErrorReceived(RssiError(rssi))
        return rssi

    @property
    def repeater_rssi(self) -> list[int]:
        """Return repeater RSSI."""
        repeater_rssi = self.data.get("repeaterRSSI", [])
        rssi_errors = [item.value for item in RssiError]
        if any(rssi_ in rssi_errors for rssi_ in repeater_rssi):
            raise RepeaterRssiErrorReceived(repeater_rssi)

        return repeater_rssi

    def as_dict(self) -> RouteStatisticsDict:
        """Return route statistics as dict."""
        return {
            "protocol_data_rate": self.protocol_data_rate.value,
            "repeaters": self.repeaters,
            "rssi": self.data.get("rssi"),
            "repeater_rssi": self.data.get("repeaterRSSI", []),
            "route_failed_between": (
                self.route_failed_between[0],
                self.route_failed_between[1],
            )
            if self.route_failed_between
            else None,
        }
