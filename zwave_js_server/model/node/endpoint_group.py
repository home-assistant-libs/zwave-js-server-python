"""Provide a model for the Z-Wave JS node's endpoint groups."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ..endpoint import Endpoint
    from . import Node


class EndpointGroupDataType(TypedDict):
    """Represent an endpoint group data dict type."""

    # https://github.com/zwave-js/zwave-js-server/blob/master/src/lib/state.ts
    id: int
    label: str
    isMainDevice: bool
    endpointIndices: list[int]


@dataclass(frozen=True)
class EndpointGroup:
    """
    Represent an endpoint group defined in the device config file.

    Endpoint groups semantically group the endpoints of a device, like the
    individual clamps of a multi-clamp energy meter.
    """

    node: Node = field(repr=False, compare=False)
    data: EndpointGroupDataType = field(repr=False)
    id: int = field(init=False)
    label: str = field(init=False)
    is_main_device: bool = field(init=False)
    # Taken as-is from the device config file and not checked against the
    # endpoints the node actually exposes. This may contain indices of endpoints
    # do not exist.
    endpoint_indices: tuple[int, ...] = field(init=False)

    def __post_init__(self) -> None:
        """Post initialize."""
        object.__setattr__(self, "id", self.data["id"])
        object.__setattr__(self, "label", self.data["label"])
        object.__setattr__(self, "is_main_device", self.data["isMainDevice"])
        object.__setattr__(
            self, "endpoint_indices", tuple(self.data["endpointIndices"])
        )

    @property
    def endpoints(self) -> list[Endpoint]:
        """Return the endpoints of this group that exist on the node."""
        return [
            self.node.endpoints[index]
            for index in self.endpoint_indices
            if index in self.node.endpoints
        ]
