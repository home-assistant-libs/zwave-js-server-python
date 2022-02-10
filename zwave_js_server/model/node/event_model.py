"""Provide a model for the Z-Wave JS node's events."""
from typing import Literal, Optional, Union

from pydantic import BaseModel

from zwave_js_server.const import CommandClass

from ...event import (
    BaseEventModel,
    _event_model_factory,
    _event_model_from_typeddict_factory,
)
from ..firmware import FirmwareUpdateFinishedDataType, FirmwareUpdateProgressDataType
from . import NodeDataType
from ..notification import (
    EntryControlNotificationArgsDataType,
    NotificationNotificationArgsDataType,
)
from .statistics import NodeStatisticsDataType
from ..value import ValueDataType


class BaseNodeEventModel(BaseEventModel):
    """Base model for a node event."""

    source: Literal["node"]
    nodeId: int


class CheckHealthProgressEventModel(BaseNodeEventModel):
    """
    Model for `check health progress` type events data.

    Includes `check lifeline health progress` and `check route health progress` events.
    """

    event: Literal["check health progress"]
    rounds: int
    total_rounds: int
    last_rating: int


class InterviewFailedEventArgsModel(BaseModel):
    """Model for `interview failed` event args."""

    errorMessage: str
    isFinal: bool
    attempt: Optional[int]
    maxAttempts: Optional[int]


class InterviewFailedEventModel(BaseNodeEventModel):
    """Model for `interview failed` event data."""

    event: Literal["interview failed"]
    args: InterviewFailedEventArgsModel


class InterviewStageCompletedEventModel(BaseNodeEventModel):
    """Model for `interview stage completed` event data."""

    event: Literal["interview stage completed"]
    stageName: str


class NotificationEventModel(BaseNodeEventModel):
    """Model for `notification` event data."""

    event: Literal["notification"]
    ccId: CommandClass
    args: Union[
        NotificationNotificationArgsDataType, EntryControlNotificationArgsDataType
    ]


class ReadyEventModel(BaseNodeEventModel):

    event: Literal["ready"]
    nodeState: NodeDataType


class StatisticsUpdatedEventModel(BaseNodeEventModel):
    """Model for `statistics updated` event data."""

    event: Literal["statistics updated"]
    statistics: NodeStatisticsDataType


class TestPowerLevelProgressEventModel(BaseNodeEventModel):
    """Model for `test powerlevel progress` event data."""

    event: Literal["test powerlevel progress"]
    acknowledged: int
    total: int


class ValueEventModel(BaseNodeEventModel):
    """
    Model for `value` events data.

    Subclass for event models for `metadata updated`, `value added`,
    `value notification`m `value removed`, and `value updated`.
    """

    value: ValueDataType


AliveEventModel = _event_model_factory(BaseEventModel, "Alive", Literal["alive"])
DeadEventModel = _event_model_factory(BaseEventModel, "Dead", Literal["dead"])
InterviewCompletedEventModel = _event_model_factory(
    BaseEventModel, "InterviewCompleted", Literal["interview completed"]
)

FirmwareUpdateFinishedEventModel = _event_model_from_typeddict_factory(
    BaseEventModel, FirmwareUpdateFinishedDataType, Literal["firmware update finished"]
)
FirmwareUpdateProgressEventModel = _event_model_from_typeddict_factory(
    BaseEventModel, FirmwareUpdateProgressDataType, Literal["firmware update progress"]
)
InterviewCompletedEventModel = _event_model_factory(
    BaseEventModel, "InterviewCompleted", Literal["interview completed"]
)
InterviewStartedEventModel = _event_model_factory(
    BaseEventModel, "InterviewStarted", Literal["interview started"]
)
MetadataUpdatedEventModel = _event_model_factory(
    ValueEventModel, "MetadataUpdated", Literal["metadata updated"]
)
SleepEventModel = _event_model_factory(BaseEventModel, "Sleep", Literal["sleep"])
ValueAddedEventModel = _event_model_factory(
    ValueEventModel, "ValueAdded", Literal["value added"]
)
ValueNotificationEventModel = _event_model_factory(
    ValueEventModel, "ValueNotification", Literal["value notification"]
)
ValueRemovedEventModel = _event_model_factory(
    ValueEventModel, "ValueRemoved", Literal["value removed"]
)
ValueUpdatedEventModel = _event_model_factory(
    ValueEventModel, "ValueUpdated", Literal["value updated"]
)
WakeUpEventModel = _event_model_factory(BaseEventModel, "WakeUp", Literal["wake up"])

NODE_EVENT_MODEL_MAP = {
    "alive": AliveEventModel,
    "check lifeline health progress": CheckHealthProgressEventModel,
    "check route health progress": CheckHealthProgressEventModel,
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
