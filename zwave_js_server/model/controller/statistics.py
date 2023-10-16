"""Provide a model for the Z-Wave JS controller's statistics."""
from __future__ import annotations

from contextlib import suppress
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

    client: Client = field(repr=False)
    data: ControllerLifelineRoutesDataType = field(repr=False)
    lwr: RouteStatistics | None = field(init=False, default=None)
    nlwr: RouteStatistics | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Post initialize."""
        if lwr := self.data.get("lwr"):
            with suppress(ValueError):
                self.lwr = RouteStatistics(self.client, lwr)
        if nlwr := self.data.get("nlwr"):
            with suppress(ValueError):
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

    data: ChannelRSSIDataType = field(repr=False)
    average: int = field(init=False)
    current: int = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        self.average = self.data["average"]
        self.current = self.data["current"]


@dataclass
class BackgroundRSSI:
    """Represent a background RSSI update."""

    data: BackgroundRSSIDataType = field(repr=False)
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

    data: ControllerStatisticsDataType = field(repr=False)
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
        self.messages_tx = self.data["messagesTX"]
        self.messages_rx = self.data["messagesRX"]
        self.messages_dropped_rx = self.data["messagesDroppedRX"]
        self.messages_dropped_tx = self.data["messagesDroppedTX"]
        self.nak = self.data["NAK"]
        self.can = self.data["CAN"]
        self.timeout_ack = self.data["timeoutACK"]
        self.timeout_response = self.data["timeoutResponse"]
        self.timeout_callback = self.data["timeoutCallback"]
        if background_rssi := self.data.get("backgroundRSSI"):
            self.background_rssi = BackgroundRSSI(background_rssi)
