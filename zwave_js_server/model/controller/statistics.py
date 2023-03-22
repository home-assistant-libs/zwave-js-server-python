"""Provide a model for the Z-Wave JS controller's statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from ..statistics import RouteStatistics, RouteStatisticsDataType

if TYPE_CHECKING:
    from ...client import Client


class ControllerLifelineRoutesDataType(TypedDict):
    """Represent a controller lifeline routes data dict type."""

    lwr: RouteStatisticsDataType
    nlwr: RouteStatisticsDataType


@dataclass
class ControllerLifelineRoutes:
    """Represent controller lifeline routes."""

    client: "Client"
    data: ControllerLifelineRoutesDataType
    lwr: RouteStatistics | None = field(init=False, default=None)
    nlwr: RouteStatistics | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post initialize."""
        if lwr := self.data.get("lwr"):
            self.lwr = RouteStatistics(self.client, lwr)
        if nlwr := self.data.get("nlwr"):
            self.nlwr = RouteStatistics(self.client, nlwr)


class ControllerStatisticsDataType(TypedDict):
    """Represent a controller statistics data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/ControllerStatistics.ts#L20-L39
    messagesTX: int
    messagesRX: int
    messagesDroppedTX: int
    messagesDroppedRX: int
    NAK: int
    CAN: int
    timeoutACK: int
    timeoutResponse: int
    timeoutCallback: int


@dataclass
class ControllerStatistics:
    """Represent a controller statistics update."""

    data: ControllerStatisticsDataType | None = None
    messages_tx: int = field(init=False)
    messages_rx: int = field(init=False)
    messages_dropped_rx: int = field(init=False)
    messages_dropped_tx: int = field(init=False)
    nak: int = field(init=False)
    can: int = field(init=False)
    timeout_ack: int = field(init=False)
    timeout_response: int = field(init=False)
    timeout_callback: int = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        data = self.data or ControllerStatisticsDataType(
            CAN=0,
            messagesDroppedRX=0,
            messagesDroppedTX=0,
            messagesRX=0,
            messagesTX=0,
            NAK=0,
            timeoutACK=0,
            timeoutCallback=0,
            timeoutResponse=0,
        )
        self.messages_tx = data["messagesTX"]
        self.messages_rx = data["messagesRX"]
        self.messages_dropped_rx = data["messagesDroppedRX"]
        self.messages_dropped_tx = data["messagesDroppedTX"]
        self.nak = data["NAK"]
        self.can = data["CAN"]
        self.timeout_ack = data["timeoutACK"]
        self.timeout_response = data["timeoutResponse"]
        self.timeout_callback = data["timeoutCallback"]
