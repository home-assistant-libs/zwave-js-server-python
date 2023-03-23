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


class ChannelRSSIDataType(TypedDict):
    """Represent a channel RSSI data dict type."""

    average: int
    current: int


class BackgroundRSSIDataType(TypedDict, total=False):
    """Represent a background RSSI data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/ControllerStatistics.ts#L40
    timestamp: int  # required
    channel0: ChannelRSSIDataType  # required
    channel1: ChannelRSSIDataType  # required
    channel2: ChannelRSSIDataType


class ControllerStatisticsDataType(TypedDict, total=False):
    """Represent a controller statistics data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/ControllerStatistics.ts#L20-L39
    messagesTX: int  # required
    messagesRX: int  # required
    messagesDroppedTX: int  # required
    messagesDroppedRX: int  # required
    NAK: int  # required
    CAN: int  # required
    timeoutACK: int  # required
    timeoutResponse: int  # required
    timeoutCallback: int  # required
    backgroundRSSI: BackgroundRSSIDataType


@dataclass
class ChannelRSSI:
    """Represent a channel RSSI."""

    data: ChannelRSSIDataType
    average: int = field(init=False)
    current: int = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.average = self.data["average"]
        self.current = self.data["current"]


@dataclass
class BackgroundRSSI:
    """Represent a background RSSI update."""

    data: BackgroundRSSIDataType
    timestamp: int = field(init=False)
    channel_0: ChannelRSSI = field(init=False)
    channel_1: ChannelRSSI = field(init=False)
    channel_2: ChannelRSSI | None = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.timestamp = self.data["timestamp"]
        self.channel_0 = ChannelRSSI(self.data["channel0"])
        self.channel_1 = ChannelRSSI(self.data["channel1"])
        if not (channel_2 := self.data.get("channel2")):
            self.channel_2 = None
            return
        self.channel_2 = ChannelRSSI(channel_2)


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
    background_rssi: BackgroundRSSI | None = field(init=False, default=None)

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
        if background_rssi := data.get("backgroundRSSI"):
            self.background_rssi = BackgroundRSSI(background_rssi)
