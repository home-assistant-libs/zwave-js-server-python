"""Provide a model for the Z-Wave JS controller's statistics."""
from __future__ import annotations

from dataclasses import dataclass
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

    def __init__(
        self, client: "Client", data: ControllerLifelineRoutesDataType
    ) -> None:
        """Initialize controller lifeline routes."""
        self.data = data
        self._lwr = None
        if lwr := self.data.get("lwr"):
            self._lwr = RouteStatistics(client, lwr)
        self._nlwr = None
        if nlwr := self.data.get("nlwr"):
            self._nlwr = RouteStatistics(client, nlwr)

    @property
    def lwr(self) -> RouteStatistics | None:
        """Return the last working route from the controller to this node."""
        return self._lwr

    @property
    def nlwr(self) -> RouteStatistics | None:
        """Return the next to last working route from the controller to this node."""
        return self._nlwr


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


class ChannelRSSI:
    """Represent a channel RSSI."""

    def __init__(self, data: ChannelRSSIDataType) -> None:
        """Initialize channel RSSI."""
        self.data = data

    @property
    def average(self) -> int:
        """Return the moving average RSSI."""
        return self.data["average"]

    @property
    def current(self) -> int:
        """Return the current RSSI."""
        return self.data["current"]


class BackgroundRSSI:
    """Represent a background RSSI update."""

    def __init__(self, data: BackgroundRSSIDataType) -> None:
        """Initialize background RSSI."""
        self.data = data

    @property
    def timestamp(self) -> int:
        """Return the timestamp of the RSSI measurement."""
        return self.data["timestamp"]

    @property
    def channel_0(self) -> ChannelRSSI:
        """Return the RSSI data for channel 0."""
        return ChannelRSSI(self.data["channel0"])

    @property
    def channel_1(self) -> ChannelRSSI:
        """Return the RSSI data for channel 1."""
        return ChannelRSSI(self.data["channel1"])

    @property
    def channel_2(self) -> Optional[ChannelRSSI]:
        """Return the RSSI data for channel 2."""
        if not (channel_2 := self.data.get("channel2")):
            return None
        return ChannelRSSI(channel_2)


class ControllerStatistics:
    """Represent a controller statistics update."""

    def __init__(self, data: ControllerStatisticsDataType | None = None) -> None:
        """Initialize controller statistics."""
        self.data = data or ControllerStatisticsDataType(
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

    @property
    def messages_tx(self) -> int:
        """Return number of messages successfully sent to controller."""
        return self.data["messagesTX"]

    @property
    def messages_rx(self) -> int:
        """Return number of messages received by controller."""
        return self.data["messagesRX"]

    @property
    def messages_dropped_rx(self) -> int:
        """Return number of messages from controller that were dropped by host."""
        return self.data["messagesDroppedRX"]

    @property
    def messages_dropped_tx(self) -> int:
        """
        Return number of outgoing messages that were dropped.

        These messages could not be sent.
        """
        return self.data["messagesDroppedTX"]

    @property
    def nak(self) -> int:
        """Return number of messages that controller did not accept."""
        return self.data["NAK"]

    @property
    def can(self) -> int:
        """Return number of collisions while sending a message to controller."""
        return self.data["CAN"]

    @property
    def timeout_ack(self) -> int:
        """Return number of transmission attempts without an ACK from controller."""
        return self.data["timeoutACK"]

    @property
    def timeout_response(self) -> int:
        """Return number of transmission attempts where controller response timed out."""
        return self.data["timeoutResponse"]

    @property
    def timeout_callback(self) -> int:
        """Return number of transmission attempts where controller callback timed out."""
        return self.data["timeoutCallback"]

    @property
    def background_rssi(self) -> Optional[BackgroundRSSI]:
        """Return background RSSI data."""
        if not (background_rssi := self.data.get("backgroundRSSI")):
            return None
        return BackgroundRSSI(background_rssi)
