"""Common models for statistics."""
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from ..const import (
    TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED,
    ProtocolDataRate,
    friendly_rssi,
)

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
        return friendly_rssi(rssi)

    @property
    def repeater_rssi(self) -> List[int]:
        """Return repeater RSSI."""
        return [friendly_rssi(rssi_) for rssi_ in self.data.get("repeaterRSSI", [])]

    @property
    def route_failed_between(self) -> Optional[List["Node"]]:
        """Return route failed between."""
        if (node_ids := self.data.get("routeFailedBetween")) is None:
            return None
        assert self.client.driver
        return [self.client.driver.controller.nodes[node_id] for node_id in node_ids]
