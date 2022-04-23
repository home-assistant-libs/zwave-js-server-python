"""Provide a model for the Z-Wave JS controller's statistics."""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ...const import TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED
from ..statistics import RouteStatistics, RouteStatisticsDataType

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

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
    def lwr(self) -> Optional[RouteStatistics]:
        """Return the last working route from the controller to this node."""
        return self._lwr

    @property
    def nlwr(self) -> Optional[RouteStatistics]:
        """Return the next to last working route from the controller to this node."""
        return self._nlwr


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


class ControllerStatistics:
    """Represent a controller statistics update."""

    def __init__(self, data: Optional[ControllerStatisticsDataType] = None) -> None:
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
