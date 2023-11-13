"""Provide a model for the Z-Wave JS controller's events."""
from __future__ import annotations

from typing import Literal, TypedDict

from ...const import RemoveNodeReason
from ...event import BaseEventModel
from ..node.data_model import FoundNodeDataType, NodeDataType
from .firmware import (
    ControllerFirmwareUpdateProgressDataType,
    ControllerFirmwareUpdateResultDataType,
)
from .inclusion_and_provisioning import InclusionGrantDataType
from .statistics import ControllerStatisticsDataType


class InclusionResultDataType(TypedDict, total=False):
    """Represent an inclusion result data dict type."""

    lowSecurity: bool  # required
    lowSecurityReason: int


class BaseControllerEventModel(BaseEventModel):
    """Base model for a controller event."""

    source: Literal["controller"]


class ExclusionFailedEventModel(BaseControllerEventModel):
    """Model for `exclusion failed` event data."""

    event: Literal["exclusion failed"]


class ExclusionStartedEventModel(BaseControllerEventModel):
    """Model for `exclusion started` event data."""

    event: Literal["exclusion started"]


class ExclusionStoppedEventModel(BaseControllerEventModel):
    """Model for `exclusion stopped` event data."""

    event: Literal["exclusion stopped"]


class FirmwareUpdateFinishedEventModel(BaseControllerEventModel):
    """Model for `firmware update finished` event data."""

    event: Literal["firmware update finished"]
    result: ControllerFirmwareUpdateResultDataType


class FirmwareUpdateProgressEventModel(BaseControllerEventModel):
    """Model for `firmware update progress` event data."""

    event: Literal["firmware update progress"]
    progress: ControllerFirmwareUpdateProgressDataType


class GrantSecurityClassesEventModel(BaseControllerEventModel):
    """Model for `grant security classes` event data."""

    event: Literal["grant security classes"]
    requested: InclusionGrantDataType


class RebuildRoutesDoneEventModel(BaseControllerEventModel):
    """Model for `rebuild routes done` event data."""

    event: Literal["rebuild routes done"]
    result: dict[str, str]


class RebuildRoutesProgressEventModel(BaseControllerEventModel):
    """Model for `rebuild routes progress` event data."""

    event: Literal["rebuild routes progress"]
    progress: dict[str, str]


class InclusionAbortedEventModel(BaseControllerEventModel):
    """Model for `inclusion aborted` event data."""

    event: Literal["inclusion aborted"]


class InclusionFailedEventModel(BaseControllerEventModel):
    """Model for `inclusion failed` event data."""

    event: Literal["inclusion failed"]


class InclusionStartedEventModel(BaseControllerEventModel):
    """Model for `inclusion started` event data."""

    event: Literal["inclusion started"]
    secure: bool


class InclusionStoppedEventModel(BaseControllerEventModel):
    """Model for `inclusion stopped` event data."""

    event: Literal["inclusion stopped"]


class NodeAddedEventModel(BaseControllerEventModel):
    """Model for `node added` event data."""

    event: Literal["node added"]
    node: NodeDataType
    result: InclusionResultDataType


class NodeFoundEventModel(BaseControllerEventModel):
    """Model for `node found` event data."""

    event: Literal["node found"]
    node: FoundNodeDataType


class NodeRemovedEventModel(BaseControllerEventModel):
    """Model for `node removed` event data."""

    event: Literal["node removed"]
    node: NodeDataType
    reason: RemoveNodeReason


class NVMBackupAndConvertProgressEventModel(BaseControllerEventModel):
    """Base model for `nvm backup progress` and `nvm convert progress` event data."""

    bytesRead: int
    total: int


class NVMBackupProgressEventModel(NVMBackupAndConvertProgressEventModel):
    """Model for `nvm backup progress` event data."""

    event: Literal["nvm backup progress"]


class NVMConvertProgressEventModel(NVMBackupAndConvertProgressEventModel):
    """Model for `nvm convert progress` event data."""

    event: Literal["nvm convert progress"]


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


class IdentifyEventModel(BaseControllerEventModel):
    """Model for `identify` event data."""

    event: Literal["identify"]
    nodeId: int


class StatusChangedEventModel(BaseControllerEventModel):
    """Model for `status changed` event data."""

    event: Literal["status changed"]
    status: int


CONTROLLER_EVENT_MODEL_MAP: dict[str, type[BaseControllerEventModel]] = {
    "exclusion failed": ExclusionFailedEventModel,
    "exclusion started": ExclusionStartedEventModel,
    "exclusion stopped": ExclusionStoppedEventModel,
    "firmware update finished": FirmwareUpdateFinishedEventModel,
    "firmware update progress": FirmwareUpdateProgressEventModel,
    "grant security classes": GrantSecurityClassesEventModel,
    "rebuild routes done": RebuildRoutesDoneEventModel,
    "rebuild routes progress": RebuildRoutesProgressEventModel,
    "identify": IdentifyEventModel,
    "inclusion aborted": InclusionAbortedEventModel,
    "inclusion failed": InclusionFailedEventModel,
    "inclusion started": InclusionStartedEventModel,
    "inclusion stopped": InclusionStoppedEventModel,
    "node added": NodeAddedEventModel,
    "node found": NodeFoundEventModel,
    "node removed": NodeRemovedEventModel,
    "nvm backup progress": NVMBackupProgressEventModel,
    "nvm convert progress": NVMConvertProgressEventModel,
    "nvm restore progress": NVMRestoreProgressEventModel,
    "statistics updated": StatisticsUpdatedEventModel,
    "status changed": StatusChangedEventModel,
    "validate dsk and enter pin": ValidateDSKAndEnterPINEventModel,
}
