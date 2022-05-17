"""Common models for statistics."""
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

from zwave_js_server.exceptions import RepeaterRssiErrorReceived, RssiErrorReceived

from ..const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED, ProtocolDataRate, RssiError

if TYPE_CHECKING:
    from ..client import Client
    from .node import Node

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class RouteStatisticsDataType(TypedDict, total=False):
    """Represent a route statistics data dict type."""

    protocolDataRate: int
    repeaters: List[int]
    rssi: int
    repeaterRSSI: List[int]
    routeFailedBetween: List[int]


class RouteStatisticsDict(TypedDict):
    """Represent a route statistics data dict type."""

    protocol_data_rate: int
    repeaters: List["Node"]
    rssi: Optional[int]
    repeater_rssi: List[int]
    route_failed_between: Optional[Tuple["Node", "Node"]]


@dataclass
class RouteStatistics:
    """Represent route statistics."""

    def __init__(self, client: "Client", data: RouteStatisticsDataType) -> None:
        """Initialize route statistics."""
        self.data = data
        self.client = client

    @property
    def protocol_data_rate(self) -> ProtocolDataRate:
        """Return protocol data rate."""
        return ProtocolDataRate(self.data["protocolDataRate"])

    @property
    def repeaters(self) -> List["Node"]:
        """Return repeaters."""
        assert self.client.driver
        return [
            self.client.driver.controller.nodes[node_id]
            for node_id in self.data["repeaters"]
        ]

    @property
    def rssi(self) -> Optional[int]:
        """Return RSSI."""
        if (rssi := self.data.get("rssi")) is None:
            return None
        if rssi in [item.value for item in RssiError]:
            raise RssiErrorReceived(RssiError(rssi))
        return rssi

    @property
    def repeater_rssi(self) -> List[int]:
        """Return repeater RSSI."""
        repeater_rssi = self.data.get("repeaterRSSI", [])
        rssi_errors = [item.value for item in RssiError]
        if any(rssi_ in rssi_errors for rssi_ in repeater_rssi):
            raise RepeaterRssiErrorReceived(repeater_rssi)

        return repeater_rssi

    @property
    def route_failed_between(self) -> Optional[Tuple["Node", "Node"]]:
        """Return route failed between."""
        if (node_ids := self.data.get("routeFailedBetween")) is None:
            return None
        assert self.client.driver
        assert len(node_ids) == 2
        return (
            self.client.driver.controller.nodes[node_ids[0]],
            self.client.driver.controller.nodes[node_ids[1]],
        )

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
