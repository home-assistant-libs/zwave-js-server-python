"""Provide a model for the Z-Wave JS controller's events."""
from typing import Dict, Literal, TypedDict

from . import InclusionGrantDataType
from .statistics import ControllerStatisticsDataType
from ...event import BaseEventModel, _event_model_factory
from ..node import NodeDataType


class BaseControllerEventModel(BaseEventModel):
    """Base model for a controller event."""

    source: Literal["controller"]


class InclusionResultDataType(TypedDict, total=False):
    """Represent an inclusion result data dict type."""

    lowSecurity: bool


class InclusionStartedEventModel(BaseControllerEventModel):
    """Model for `inclusion started` event data."""

    event: Literal["inclusion started"]
    secure: bool


class GrantSecurityClassesEventModel(BaseControllerEventModel):
    """Model for `grant security classes` event data."""

    event: Literal["grant security classes"]
    requested: InclusionGrantDataType


class HealNetworkDoneEventModel(BaseControllerEventModel):
    """Model for `heal network done` event data."""

    event: Literal["heal network done"]
    result: Dict[int, str]


class HealNetworkProgressEventModel(BaseControllerEventModel):
    """Model for `heal network progress` event data."""

    event: Literal["heal network progress"]
    progress: Dict[int, str]


class NodeAddedEventModel(BaseControllerEventModel):
    """Model for `node added` event data."""

    event: Literal["node added"]
    node: NodeDataType
    result: InclusionResultDataType


class NodeRemovedEventModel(BaseControllerEventModel):
    """Model for `node removed` event data."""

    event: Literal["node removed"]
    node: NodeDataType
    replaced: bool


class NVMBackupAndConvertProgressEventModel(BaseControllerEventModel):
    """Model for `nvm backup progress` and `nvm convert progress` event data."""

    bytesRead: int
    total: int


class NVMRestoreProgressEventModel(BaseControllerEventModel):
    """Model for `nvm restore progress` event data."""

    event: Literal["nvm restore progress"]
    bytesWritten: int
    total: int


class StatisticsUpdatedEventModel(BaseControllerEventModel):
    """Model for `statistics updated` event data."""

    event: Literal["statistics updated"]
    statistics: ControllerStatisticsDataType


class ValidateDSKAndEnterPINEventModel(BaseControllerEventModel):
    """Model for `validate dsk and enter pin` event data."""

    event: Literal["validate dsk and enter pin"]
    dsk: str


ExclusionFailedEventModel = _event_model_factory(
    BaseControllerEventModel, "ExclusionFailed", Literal["exclusion failed"]
)
ExclusionStartedEventModel = _event_model_factory(
    BaseControllerEventModel, "ExclusionStarted", Literal["exclusion started"]
)
ExclusionStoppedEventModel = _event_model_factory(
    BaseControllerEventModel, "ExclusionStopped", Literal["exclusion stopped"]
)
InclusionFailedEventModel = _event_model_factory(
    BaseControllerEventModel, "InclusionFailed", Literal["inclusion failed"]
)
InclusionStoppedEventModel = _event_model_factory(
    BaseControllerEventModel, "InclusionStarted", Literal["inclusion started"]
)
NVMBackupProgressEventModel = _event_model_factory(
    NVMBackupAndConvertProgressEventModel,
    "NVMBackupProgressController",
    Literal["nvm backup progress"],
)
NVMConvertProgressEventModel = _event_model_factory(
    NVMBackupAndConvertProgressEventModel,
    "NVMConvertProgressController",
    Literal["nvm backup progress"],
)


CONTROLLER_EVENT_MODEL_MAP = {
    "exclusion failed": ExclusionFailedEventModel,
    "exclusion started": ExclusionStartedEventModel,
    "exclusion stopped": ExclusionStoppedEventModel,
    "grant security classes": GrantSecurityClassesEventModel,
    "heal network done": HealNetworkDoneEventModel,
    "heal network progress": HealNetworkProgressEventModel,
    "inclusion failed": InclusionFailedEventModel,
    "inclusion started": InclusionStartedEventModel,
    "inclusion stopped": InclusionStoppedEventModel,
    "node added": NodeAddedEventModel,
    "node removed": NodeRemovedEventModel,
    "nvm backup progress": NVMBackupProgressEventModel,
    "nvm convert progress": NVMConvertProgressEventModel,
    "nvm restore progress": NVMRestoreProgressEventModel,
    "statistics updated": StatisticsUpdatedEventModel,
    "validate dsk and enter pin": ValidateDSKAndEnterPINEventModel,
}
