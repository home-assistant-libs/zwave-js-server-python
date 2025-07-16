"""Provide a model for the Z-Wave JS node's events."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from ...const import CommandClass
from ...event import BaseEventModel
from ..notification import (
    EntryControlNotificationArgsDataType,
    MultilevelSwitchNotificationArgsDataType,
    NotificationNotificationArgsDataType,
    PowerLevelNotificationArgsDataType,
)
from ..value import ValueDataType
from .data_model import NodeDataType
from .firmware import (
    NodeFirmwareUpdateProgressDataType,
    NodeFirmwareUpdateResultDataType,
)
from .statistics import NodeStatisticsDataType


class BaseNodeEventModel(BaseEventModel):
    """Base model for a node event."""

    source: Literal["node"]
    nodeId: int

    @classmethod
    def from_dict(cls, data: dict) -> BaseNodeEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
        )


class AliveEventModel(BaseNodeEventModel):
    """Model for `alive` event data."""

    event: Literal["alive"]


class CheckHealthProgressEventModel(BaseNodeEventModel):
    """
    Model for `check health progress` type events data.

    Includes `check lifeline health progress` and `check route health progress` events.
    """

    rounds: int
    totalRounds: int
    lastRating: int

    @classmethod
    def from_dict(cls, data: dict) -> CheckHealthProgressEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            rounds=data["rounds"],
            totalRounds=data["totalRounds"],
            lastRating=data["lastRating"],
        )


class CheckLifelineHealthProgressEventModel(CheckHealthProgressEventModel):
    """Model for `check lifeline health progress` event data."""

    event: Literal["check lifeline health progress"]


class CheckRouteHealthProgressEventModel(CheckHealthProgressEventModel):
    """Model for `check route health progress` event data."""

    event: Literal["check route health progress"]


class DeadEventModel(BaseNodeEventModel):
    """Model for `dead` event data."""

    event: Literal["dead"]


class InterviewCompletedEventModel(BaseNodeEventModel):
    """Model for `interview completed` event data."""

    event: Literal["interview completed"]


class InterviewFailedEventArgsModel(BaseModel):
    """Model for `interview failed` event args."""

    errorMessage: str
    isFinal: bool
    attempt: int | None = None
    maxAttempts: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> InterviewFailedEventArgsModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            errorMessage=data["errorMessage"],
            isFinal=data["isFinal"],
            attempt=data["attempt"],
            maxAttempts=data["maxAttempts"],
        )


class InterviewFailedEventModel(BaseNodeEventModel):
    """Model for `interview failed` event data."""

    event: Literal["interview failed"]
    args: InterviewFailedEventArgsModel

    @classmethod
    def from_dict(cls, data: dict) -> InterviewFailedEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            args=data["args"],
        )


class InterviewStageCompletedEventModel(BaseNodeEventModel):
    """Model for `interview stage completed` event data."""

    event: Literal["interview stage completed"]
    stageName: str

    @classmethod
    def from_dict(cls, data: dict) -> InterviewStageCompletedEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            stageName=data["stageName"],
        )


class InterviewStartedEventModel(BaseNodeEventModel):
    """Model for `interview started` event data."""

    event: Literal["interview started"]


class NotificationEventModel(BaseNodeEventModel):
    """Model for `notification` event data."""

    event: Literal["notification"]
    nodeId: int
    endpointIndex: int
    ccId: CommandClass
    args: (
        NotificationNotificationArgsDataType
        | EntryControlNotificationArgsDataType
        | PowerLevelNotificationArgsDataType
        | MultilevelSwitchNotificationArgsDataType
    )

    @classmethod
    def from_dict(cls, data: dict) -> NotificationEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            endpointIndex=data["endpointIndex"],
            ccId=data["ccId"],
            args=data["args"],
        )


class ReadyEventModel(BaseNodeEventModel):
    """Model for `ready` event data."""

    event: Literal["ready"]
    nodeState: NodeDataType

    @classmethod
    def from_dict(cls, data: dict) -> ReadyEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            nodeState=data["nodeState"],
        )


class SleepEventModel(BaseNodeEventModel):
    """Model for `sleep` event data."""

    event: Literal["sleep"]


class StatisticsUpdatedEventModel(BaseNodeEventModel):
    """Model for `statistics updated` event data."""

    event: Literal["statistics updated"]
    statistics: NodeStatisticsDataType

    @classmethod
    def from_dict(cls, data: dict) -> StatisticsUpdatedEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            statistics=data["statistics"],
        )


class TestPowerLevelProgressEventModel(BaseNodeEventModel):
    """Model for `test powerlevel progress` event data."""

    event: Literal["test powerlevel progress"]
    acknowledged: int
    total: int

    @classmethod
    def from_dict(cls, data: dict) -> TestPowerLevelProgressEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            acknowledged=data["acknowledged"],
            total=data["total"],
        )


class ValueEventModel(BaseNodeEventModel):
    """
    Model for `value` events data.

    Subclass for event models for `metadata updated`, `value added`,
    `value notification`, `value removed`, and `value updated`.
    """

    args: ValueDataType

    @classmethod
    def from_dict(cls, data: dict) -> ValueEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            args=data["args"],
        )


class MetadataUpdatedEventModel(ValueEventModel):
    """Model for `metadata updated` event data."""

    event: Literal["metadata updated"]


class ValueAddedEventModel(ValueEventModel):
    """Model for `value added` event data."""

    event: Literal["value added"]


class ValueNotificationEventModel(ValueEventModel):
    """Model for `value notification` event data."""

    event: Literal["value notification"]


class ValueRemovedEventModel(ValueEventModel):
    """Model for `value removed` event data."""

    event: Literal["value removed"]


class ValueUpdatedEventModel(ValueEventModel):
    """Model for `value updated` event data."""

    event: Literal["value updated"]


class WakeUpEventModel(BaseNodeEventModel):
    """Model for `wake up` event data."""

    event: Literal["wake up"]


class FirmwareUpdateFinishedEventModel(BaseNodeEventModel):
    """Model for `firmware update finished` event data."""

    event: Literal["firmware update finished"]
    result: NodeFirmwareUpdateResultDataType

    @classmethod
    def from_dict(cls, data: dict) -> FirmwareUpdateFinishedEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            result=data["result"],
        )


class FirmwareUpdateProgressEventModel(BaseNodeEventModel):
    """Model for `firmware update progress` event data."""

    event: Literal["firmware update progress"]
    progress: NodeFirmwareUpdateProgressDataType

    @classmethod
    def from_dict(cls, data: dict) -> FirmwareUpdateProgressEventModel:
        """Initialize from dict."""
        return cls(
            source=data["source"],
            event=data["event"],
            nodeId=data["nodeId"],
            progress=data["progress"],
        )


NODE_EVENT_MODEL_MAP: dict[str, type[BaseNodeEventModel]] = {
    "alive": AliveEventModel,
    "check lifeline health progress": CheckLifelineHealthProgressEventModel,
    "check route health progress": CheckRouteHealthProgressEventModel,
    "dead": DeadEventModel,
    "firmware update finished": FirmwareUpdateFinishedEventModel,
    "firmware update progress": FirmwareUpdateProgressEventModel,
    "interview completed": InterviewCompletedEventModel,
    "interview failed": InterviewFailedEventModel,
    "interview stage completed": InterviewStageCompletedEventModel,
    "interview started": InterviewStartedEventModel,
    "metadata updated": MetadataUpdatedEventModel,
    "notification": NotificationEventModel,
    "ready": ReadyEventModel,
    "sleep": SleepEventModel,
    "statistics updated": StatisticsUpdatedEventModel,
    "test powerlevel progress": TestPowerLevelProgressEventModel,
    "value added": ValueAddedEventModel,
    "value notification": ValueNotificationEventModel,
    "value removed": ValueRemovedEventModel,
    "value updated": ValueUpdatedEventModel,
    "wake up": WakeUpEventModel,
}
