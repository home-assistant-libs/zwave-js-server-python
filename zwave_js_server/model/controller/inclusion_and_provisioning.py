"""Provide a model for the Z-Wave JS controller's inclusion/provisioning data structures."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...const import (
    TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED,
    Protocols,
    ProvisioningEntryStatus,
    QRCodeVersion,
    SecurityClass,
)

if TYPING_EXTENSION_FOR_TYPEDDICT_REQUIRED:
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class InclusionGrantDataType(TypedDict):
    """Representation of an inclusion grant data dict type."""

    # https://github.com/zwave-js/node-zwave-js/blob/master/packages/zwave-js/src/lib/controller/Inclusion.ts#L48-L56
    securityClasses: List[int]
    clientSideAuth: bool


@dataclass
class InclusionGrant:
    """Representation of an inclusion grant."""

    security_classes: List[SecurityClass]
    client_side_auth: bool

    def to_dict(self) -> InclusionGrantDataType:
        """Return InclusionGrantDataType dict from self."""
        return {
            "securityClasses": [sec_cls.value for sec_cls in self.security_classes],
            "clientSideAuth": self.client_side_auth,
        }

    @classmethod
    def from_dict(cls, data: InclusionGrantDataType) -> "InclusionGrant":
        """Return InclusionGrant from InclusionGrantDataType dict."""
        return cls(
            security_classes=[
                SecurityClass(sec_cls) for sec_cls in data["securityClasses"]
            ],
            client_side_auth=data["clientSideAuth"],
        )


@dataclass
class ProvisioningEntry:
    """Class to represent the base fields of a provisioning entry."""

    dsk: str
    security_classes: List[SecurityClass]
    requested_security_classes: List[SecurityClass] = field(default_factory=list)
    status: ProvisioningEntryStatus = ProvisioningEntryStatus.ACTIVE
    additional_properties: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return PlannedProvisioning data dict from self."""
        return {
            "dsk": self.dsk,
            "securityClasses": [sec_cls.value for sec_cls in self.security_classes],
            "requestedSecurityClasses": [
                sec_cls.value for sec_cls in self.requested_security_classes
            ],
            "status": self.status.value,
            **(self.additional_properties or {}),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvisioningEntry":
        """Return ProvisioningEntry from data dict."""
        cls_instance = cls(
            dsk=data["dsk"],
            security_classes=[
                SecurityClass(sec_cls) for sec_cls in data["securityClasses"]
            ],
            requested_security_classes=[
                SecurityClass(sec_cls)
                for sec_cls in data.get("requestedSecurityClasses", [])
            ],
            additional_properties={
                k: v
                for k, v in data.items()
                if k not in {"dsk", "securityClasses", "requestedSecurityClasses"}
            },
        )
        if "status" in data:
            cls_instance.status = ProvisioningEntryStatus(data["status"])
        return cls_instance


@dataclass
class QRProvisioningInformationMixin:
    """Mixin class to represent the base fields of a QR provisioning information."""

    version: QRCodeVersion
    generic_device_class: int
    specific_device_class: int
    installer_icon_type: int
    manufacturer_id: int
    product_type: int
    product_id: int
    application_version: str
    max_inclusion_request_interval: Optional[int]
    uuid: Optional[str]
    supported_protocols: Optional[List[Protocols]]


@dataclass
class QRProvisioningInformation(ProvisioningEntry, QRProvisioningInformationMixin):
    """Representation of provisioning information retrieved from a QR code."""

    def to_dict(self) -> Dict[str, Any]:
        """Return QRProvisioningInformation data dict from self."""
        data = {
            "version": self.version.value,
            "securityClasses": [sec_cls.value for sec_cls in self.security_classes],
            "requestedSecurityClasses": [
                sec_cls.value for sec_cls in self.requested_security_classes
            ],
            "dsk": self.dsk,
            "genericDeviceClass": self.generic_device_class,
            "specificDeviceClass": self.specific_device_class,
            "installerIconType": self.installer_icon_type,
            "manufacturerId": self.manufacturer_id,
            "productType": self.product_type,
            "productId": self.product_id,
            "applicationVersion": self.application_version,
            **(self.additional_properties or {}),
        }
        if self.max_inclusion_request_interval is not None:
            data["maxInclusionRequestInterval"] = self.max_inclusion_request_interval
        if self.uuid is not None:
            data["uuid"] = self.uuid
        if self.supported_protocols is not None:
            data["supportedProtocols"] = [
                protocol.value for protocol in self.supported_protocols
            ]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QRProvisioningInformation":
        """Return QRProvisioningInformation from data dict."""
        return cls(
            version=QRCodeVersion(data["version"]),
            security_classes=[
                SecurityClass(sec_cls) for sec_cls in data["securityClasses"]
            ],
            requested_security_classes=[
                SecurityClass(sec_cls)
                for sec_cls in data.get("requestedSecurityClasses", [])
            ],
            dsk=data["dsk"],
            generic_device_class=data["genericDeviceClass"],
            specific_device_class=data["specificDeviceClass"],
            installer_icon_type=data["installerIconType"],
            manufacturer_id=data["manufacturerId"],
            product_type=data["productType"],
            product_id=data["productId"],
            application_version=data["applicationVersion"],
            max_inclusion_request_interval=data.get("maxInclusionRequestInterval"),
            uuid=data.get("uuid"),
            supported_protocols=[
                Protocols(supported_protocol)
                for supported_protocol in data.get("supportedProtocols", [])
            ],
            additional_properties={
                k: v
                for k, v in data.items()
                if k
                not in {
                    "version",
                    "securityClasses",
                    "requestedSecurityClasses",
                    "dsk",
                    "genericDeviceClass",
                    "specificDeviceClass",
                    "installerIconType",
                    "manufacturerId",
                    "productType",
                    "productId",
                    "applicationVersion",
                    "maxInclusionRequestInterval",
                    "uuid",
                    "supportedProtocols",
                }
            },
        )
