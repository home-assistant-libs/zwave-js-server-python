"""Shared models and API wrapper for endpoint access-control support."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypedDict, cast

from ..const.command_class.access_control import (
    AssignCredentialResult,
    SetCredentialResult,
    SetUserResult,
    UserCredentialLearnStatus,
    UserCredentialRule,
    UserCredentialType,
    UserCredentialUserType,
)
from ..util.helpers import (
    BufferObjectDataType,
    buffer_object_to_bytes,
    bytes_to_buffer_object,
)
from .value import SupervisionResult, parse_supervision_result

if TYPE_CHECKING:
    from .endpoint import Endpoint


def serialize_credential_data(data: str | bytes) -> str | BufferObjectDataType:
    """Serialize a credential payload for websocket transport."""
    if isinstance(data, bytes):
        return bytes_to_buffer_object(data)
    return data


def deserialize_credential_data(
    data: str | BufferObjectDataType | None,
) -> str | bytes | None:
    """Deserialize a credential payload from websocket transport."""
    if data is None:
        return None
    if isinstance(data, str):
        return data
    return buffer_object_to_bytes(data)


class UserCredentialCapabilityDataType(TypedDict, total=False):
    """Represent a credential capability payload."""

    numberOfCredentialSlots: int
    minCredentialLength: int
    maxCredentialLength: int
    maxCredentialHashLength: int
    supportsCredentialLearn: bool
    credentialLearnRecommendedTimeout: int
    credentialLearnNumberOfSteps: int


@dataclass
class UserCredentialCapability:
    """Credential capability for a single credential type."""

    number_of_credential_slots: int
    min_credential_length: int
    max_credential_length: int
    max_credential_hash_length: int
    supports_credential_learn: bool
    credential_learn_recommended_timeout: int | None = None
    credential_learn_number_of_steps: int | None = None

    @classmethod
    def from_dict(
        cls, data: UserCredentialCapabilityDataType
    ) -> UserCredentialCapability:
        """Return capability from serialized data."""
        return cls(
            number_of_credential_slots=data["numberOfCredentialSlots"],
            min_credential_length=data["minCredentialLength"],
            max_credential_length=data["maxCredentialLength"],
            max_credential_hash_length=data["maxCredentialHashLength"],
            supports_credential_learn=data["supportsCredentialLearn"],
            credential_learn_recommended_timeout=data.get(
                "credentialLearnRecommendedTimeout"
            ),
            credential_learn_number_of_steps=data.get("credentialLearnNumberOfSteps"),
        )

    def to_dict(self) -> UserCredentialCapabilityDataType:
        """Return serialized capability data."""
        data: UserCredentialCapabilityDataType = {
            "numberOfCredentialSlots": self.number_of_credential_slots,
            "minCredentialLength": self.min_credential_length,
            "maxCredentialLength": self.max_credential_length,
            "maxCredentialHashLength": self.max_credential_hash_length,
            "supportsCredentialLearn": self.supports_credential_learn,
        }
        if self.credential_learn_recommended_timeout is not None:
            data["credentialLearnRecommendedTimeout"] = (
                self.credential_learn_recommended_timeout
            )
        if self.credential_learn_number_of_steps is not None:
            data["credentialLearnNumberOfSteps"] = self.credential_learn_number_of_steps
        return data


class UserCapabilitiesDataType(TypedDict, total=False):
    """Represent user capabilities payload."""

    maxUsers: int
    supportedUserTypes: list[UserCredentialUserType]
    maxUserNameLength: int
    supportedCredentialRules: list[UserCredentialRule]


@dataclass
class UserCapabilities:
    """User-related capabilities for an access-control endpoint."""

    max_users: int
    supported_user_types: list[UserCredentialUserType] = field(default_factory=list)
    max_user_name_length: int | None = None
    supported_credential_rules: list[UserCredentialRule] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: UserCapabilitiesDataType) -> UserCapabilities:
        """Return user capabilities from serialized data."""
        return cls(
            max_users=data["maxUsers"],
            supported_user_types=[
                UserCredentialUserType(user_type)
                for user_type in data.get("supportedUserTypes", [])
            ],
            max_user_name_length=data.get("maxUserNameLength"),
            supported_credential_rules=[
                UserCredentialRule(rule)
                for rule in data.get("supportedCredentialRules", [])
            ],
        )

    def to_dict(self) -> UserCapabilitiesDataType:
        """Return serialized user capabilities."""
        data: UserCapabilitiesDataType = {
            "maxUsers": self.max_users,
            "supportedUserTypes": list(self.supported_user_types),
            "supportedCredentialRules": list(self.supported_credential_rules),
        }
        if self.max_user_name_length is not None:
            data["maxUserNameLength"] = self.max_user_name_length
        return data


class CredentialCapabilitiesDataType(TypedDict, total=False):
    """Represent credential capabilities payload."""

    supportedCredentialTypes: dict[str, UserCredentialCapabilityDataType]
    supportsAdminCode: bool
    supportsAdminCodeDeactivation: bool
    supportsCredentialAssignment: bool


@dataclass
class CredentialCapabilities:
    """Credential-related capabilities for an access-control endpoint."""

    supported_credential_types: dict[UserCredentialType, UserCredentialCapability] = (
        field(default_factory=dict)
    )
    supports_admin_code: bool = False
    supports_admin_code_deactivation: bool = False
    supports_credential_assignment: bool = False

    @classmethod
    def from_dict(cls, data: CredentialCapabilitiesDataType) -> CredentialCapabilities:
        """Return credential capabilities from serialized data."""
        supported_credential_types = {
            UserCredentialType(
                int(credential_type)
            ): UserCredentialCapability.from_dict(capability)
            for credential_type, capability in data.get(
                "supportedCredentialTypes", {}
            ).items()
        }
        return cls(
            supported_credential_types=supported_credential_types,
            supports_admin_code=data.get("supportsAdminCode", False),
            supports_admin_code_deactivation=data.get(
                "supportsAdminCodeDeactivation", False
            ),
            supports_credential_assignment=data.get(
                "supportsCredentialAssignment", False
            ),
        )

    def to_dict(self) -> CredentialCapabilitiesDataType:
        """Return serialized credential capabilities."""
        return {
            "supportedCredentialTypes": {
                str(int(credential_type)): capability.to_dict()
                for credential_type, capability in self.supported_credential_types.items()
            },
            "supportsAdminCode": self.supports_admin_code,
            "supportsAdminCodeDeactivation": self.supports_admin_code_deactivation,
            "supportsCredentialAssignment": self.supports_credential_assignment,
        }


class UserDataDataType(TypedDict, total=False):
    """Represent access-control user payload."""

    userId: int
    active: bool
    userType: UserCredentialUserType
    userName: str
    credentialRule: UserCredentialRule
    expiringTimeoutMinutes: int


@dataclass
class UserData:
    """User data returned by endpoint access-control commands."""

    user_id: int
    active: bool
    user_type: UserCredentialUserType
    user_name: str | None = None
    credential_rule: UserCredentialRule | None = None
    expiring_timeout_minutes: int | None = None

    @classmethod
    def from_dict(cls, data: UserDataDataType) -> UserData:
        """Return user data from serialized payload."""
        return cls(
            user_id=data["userId"],
            active=data.get("active", False),
            user_type=UserCredentialUserType(data.get("userType", 0)),
            user_name=data.get("userName"),
            credential_rule=(
                UserCredentialRule(credential_rule)
                if (credential_rule := data.get("credentialRule")) is not None
                else None
            ),
            expiring_timeout_minutes=data.get("expiringTimeoutMinutes"),
        )

    def to_dict(self) -> UserDataDataType:
        """Return serialized user payload."""
        data: UserDataDataType = {
            "userId": self.user_id,
            "active": self.active,
            "userType": self.user_type,
        }
        if self.user_name is not None:
            data["userName"] = self.user_name
        if self.credential_rule is not None:
            data["credentialRule"] = self.credential_rule
        if self.expiring_timeout_minutes is not None:
            data["expiringTimeoutMinutes"] = self.expiring_timeout_minutes
        return data


class SetUserOptionsDataType(TypedDict, total=False):
    """Represent serialized set-user options."""

    active: bool
    userType: UserCredentialUserType
    userName: str
    credentialRule: UserCredentialRule
    expiringTimeoutMinutes: int


@dataclass
class SetUserOptions:
    """Options for creating or updating a user."""

    active: bool | None = None
    user_type: UserCredentialUserType | None = None
    user_name: str | None = None
    credential_rule: UserCredentialRule | None = None
    expiring_timeout_minutes: int | None = None

    def to_dict(self) -> SetUserOptionsDataType:
        """Return serialized set-user options."""
        data: SetUserOptionsDataType = {}
        if self.active is not None:
            data["active"] = self.active
        if self.user_type is not None:
            data["userType"] = self.user_type
        if self.user_name is not None:
            data["userName"] = self.user_name
        if self.credential_rule is not None:
            data["credentialRule"] = self.credential_rule
        if self.expiring_timeout_minutes is not None:
            data["expiringTimeoutMinutes"] = self.expiring_timeout_minutes
        return data


class CredentialDataDataType(TypedDict, total=False):
    """Represent access-control credential payload."""

    userId: int
    type: UserCredentialType
    slot: int
    data: str | BufferObjectDataType


@dataclass
class CredentialData:
    """Credential data returned by endpoint access-control commands."""

    user_id: int
    type: UserCredentialType
    slot: int
    data: str | bytes | None = None

    @classmethod
    def from_dict(cls, data: CredentialDataDataType) -> CredentialData:
        """Return credential data from serialized payload."""
        return cls(
            user_id=data["userId"],
            type=UserCredentialType(data["type"]),
            slot=data["slot"],
            data=deserialize_credential_data(data.get("data")),
        )

    def to_dict(self) -> CredentialDataDataType:
        """Return serialized credential payload."""
        data: CredentialDataDataType = {
            "userId": self.user_id,
            "type": self.type,
            "slot": self.slot,
        }
        if self.data is not None:
            data["data"] = serialize_credential_data(self.data)
        return data


class UserDeletedArgsDataType(TypedDict):
    """Represent access-control user deleted event args."""

    userId: int


@dataclass
class UserDeletedArgs:
    """Args for access-control user deleted events."""

    user_id: int

    @classmethod
    def from_dict(cls, data: UserDeletedArgsDataType) -> UserDeletedArgs:
        """Return user deleted args from serialized payload."""
        return cls(user_id=data["userId"])

    def to_dict(self) -> UserDeletedArgsDataType:
        """Return serialized user deleted args."""
        return {"userId": self.user_id}


class CredentialChangedArgsDataType(TypedDict, total=False):
    """Represent access-control credential changed event args."""

    userId: int
    credentialType: UserCredentialType
    credentialSlot: int
    data: str | BufferObjectDataType


@dataclass
class CredentialChangedArgs:
    """Args for access-control credential add/modify events."""

    user_id: int
    credential_type: UserCredentialType
    credential_slot: int
    data: str | bytes | None = None

    @classmethod
    def from_dict(cls, data: CredentialChangedArgsDataType) -> CredentialChangedArgs:
        """Return credential changed args from serialized payload."""
        return cls(
            user_id=data["userId"],
            credential_type=UserCredentialType(data["credentialType"]),
            credential_slot=data["credentialSlot"],
            data=deserialize_credential_data(data.get("data")),
        )

    def to_dict(self) -> CredentialChangedArgsDataType:
        """Return serialized credential changed args."""
        data: CredentialChangedArgsDataType = {
            "userId": self.user_id,
            "credentialType": self.credential_type,
            "credentialSlot": self.credential_slot,
        }
        if self.data is not None:
            data["data"] = serialize_credential_data(self.data)
        return data


class CredentialDeletedArgsDataType(TypedDict):
    """Represent access-control credential deleted event args."""

    userId: int
    credentialType: UserCredentialType
    credentialSlot: int


@dataclass
class CredentialDeletedArgs:
    """Args for access-control credential deleted events."""

    user_id: int
    credential_type: UserCredentialType
    credential_slot: int

    @classmethod
    def from_dict(cls, data: CredentialDeletedArgsDataType) -> CredentialDeletedArgs:
        """Return credential deleted args from serialized payload."""
        return cls(
            user_id=data["userId"],
            credential_type=UserCredentialType(data["credentialType"]),
            credential_slot=data["credentialSlot"],
        )

    def to_dict(self) -> CredentialDeletedArgsDataType:
        """Return serialized credential deleted args."""
        return {
            "userId": self.user_id,
            "credentialType": self.credential_type,
            "credentialSlot": self.credential_slot,
        }


class CredentialLearnProgressArgsDataType(TypedDict):
    """Represent access-control credential learn progress event args."""

    userId: int
    credentialType: UserCredentialType
    credentialSlot: int
    stepsRemaining: int
    status: UserCredentialLearnStatus


@dataclass
class CredentialLearnProgressArgs:
    """Args for access-control credential learn progress events."""

    user_id: int
    credential_type: UserCredentialType
    credential_slot: int
    steps_remaining: int
    status: UserCredentialLearnStatus

    @classmethod
    def from_dict(
        cls, data: CredentialLearnProgressArgsDataType
    ) -> CredentialLearnProgressArgs:
        """Return credential learn progress args from serialized payload."""
        return cls(
            user_id=data["userId"],
            credential_type=UserCredentialType(data["credentialType"]),
            credential_slot=data["credentialSlot"],
            steps_remaining=data["stepsRemaining"],
            status=UserCredentialLearnStatus(data["status"]),
        )

    def to_dict(self) -> CredentialLearnProgressArgsDataType:
        """Return serialized credential learn progress args."""
        return {
            "userId": self.user_id,
            "credentialType": self.credential_type,
            "credentialSlot": self.credential_slot,
            "stepsRemaining": self.steps_remaining,
            "status": self.status,
        }


class CredentialLearnCompletedArgsDataType(TypedDict):
    """Represent access-control credential learn completed event args."""

    userId: int
    credentialType: UserCredentialType
    credentialSlot: int
    status: UserCredentialLearnStatus
    success: bool


@dataclass
class CredentialLearnCompletedArgs:
    """Args for access-control credential learn completed events."""

    user_id: int
    credential_type: UserCredentialType
    credential_slot: int
    status: UserCredentialLearnStatus
    success: bool

    @classmethod
    def from_dict(
        cls, data: CredentialLearnCompletedArgsDataType
    ) -> CredentialLearnCompletedArgs:
        """Return credential learn completed args from serialized payload."""
        return cls(
            user_id=data["userId"],
            credential_type=UserCredentialType(data["credentialType"]),
            credential_slot=data["credentialSlot"],
            status=UserCredentialLearnStatus(data["status"]),
            success=data["success"],
        )

    def to_dict(self) -> CredentialLearnCompletedArgsDataType:
        """Return serialized credential learn completed args."""
        return {
            "userId": self.user_id,
            "credentialType": self.credential_type,
            "credentialSlot": self.credential_slot,
            "status": self.status,
            "success": self.success,
        }


class AccessControlAPI:
    """Access-control command API wrapper for a single endpoint.

    Schema 48+. Obtain via :attr:`Endpoint.access_control` or
    :attr:`Node.access_control` (root endpoint shortcut).
    """

    def __init__(self, endpoint: Endpoint) -> None:
        """Initialize the API wrapper for the given endpoint."""
        self._endpoint = endpoint

    async def is_supported(self) -> bool:
        """Return whether the endpoint supports access-control methods."""
        result = await self._endpoint.async_send_command(
            "access_control.is_supported",
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        return cast(bool, result["supported"])

    async def get_user_capabilities_cached(self) -> UserCapabilities:
        """Return cached user capabilities for access control."""
        result = await self._endpoint.async_send_command(
            "access_control.get_user_capabilities_cached",
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        capabilities = result["capabilities"]
        assert capabilities is not None
        return UserCapabilities.from_dict(cast(UserCapabilitiesDataType, capabilities))

    async def get_credential_capabilities_cached(
        self,
    ) -> CredentialCapabilities:
        """Return cached credential capabilities for access control."""
        result = await self._endpoint.async_send_command(
            "access_control.get_credential_capabilities_cached",
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        capabilities = result["capabilities"]
        assert capabilities is not None
        return CredentialCapabilities.from_dict(
            cast(CredentialCapabilitiesDataType, capabilities)
        )

    async def get_user(self, user_id: int) -> UserData | None:
        """Return fresh data for a single access-control user."""
        result = await self._endpoint.async_send_command(
            "access_control.get_user",
            userId=user_id,
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        if (user := result.get("user")) is None:
            return None
        return UserData.from_dict(cast(UserDataDataType, user))

    async def get_user_cached(self, user_id: int) -> UserData | None:
        """Return cached data for a single access-control user."""
        result = await self._endpoint.async_send_command(
            "access_control.get_user_cached",
            userId=user_id,
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        if (user := result.get("user")) is None:
            return None
        return UserData.from_dict(cast(UserDataDataType, user))

    async def get_users(self) -> list[UserData]:
        """Return fresh data for all configured access-control users."""
        result = await self._endpoint.async_send_command(
            "access_control.get_users",
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        users = result["users"]
        assert users is not None
        return [UserData.from_dict(cast(UserDataDataType, user)) for user in users]

    async def get_users_cached(self) -> list[UserData]:
        """Return cached data for all configured access-control users."""
        result = await self._endpoint.async_send_command(
            "access_control.get_users_cached",
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        users = result["users"]
        assert users is not None
        return [UserData.from_dict(cast(UserDataDataType, user)) for user in users]

    async def set_user(self, user_id: int, options: SetUserOptions) -> SetUserResult:
        """Create or update an access-control user."""
        result = await self._endpoint.async_send_command(
            "access_control.set_user",
            userId=user_id,
            options=options.to_dict(),
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        return SetUserResult(result["result"])

    async def delete_user(self, user_id: int) -> SetUserResult:
        """Delete an access-control user."""
        result = await self._endpoint.async_send_command(
            "access_control.delete_user",
            userId=user_id,
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        return SetUserResult(result["result"])

    async def delete_all_users(self) -> SetUserResult:
        """Delete all configured access-control users."""
        result = await self._endpoint.async_send_command(
            "access_control.delete_all_users",
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        return SetUserResult(result["result"])

    async def get_credential(
        self,
        credential_type: UserCredentialType,
        credential_slot: int,
    ) -> CredentialData | None:
        """Return fresh data for a single access-control credential."""
        result = await self._endpoint.async_send_command(
            "access_control.get_credential",
            credentialType=credential_type,
            credentialSlot=credential_slot,
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        if (credential := result.get("credential")) is None:
            return None
        return CredentialData.from_dict(cast(CredentialDataDataType, credential))

    async def get_credential_cached(
        self,
        credential_type: UserCredentialType,
        credential_slot: int,
    ) -> CredentialData | None:
        """Return cached data for a single access-control credential."""
        result = await self._endpoint.async_send_command(
            "access_control.get_credential_cached",
            credentialType=credential_type,
            credentialSlot=credential_slot,
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        if (credential := result.get("credential")) is None:
            return None
        return CredentialData.from_dict(cast(CredentialDataDataType, credential))

    async def get_credentials(self, user_id: int) -> list[CredentialData]:
        """Return fresh data for all credentials assigned to a user."""
        result = await self._endpoint.async_send_command(
            "access_control.get_credentials",
            userId=user_id,
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        credentials = result["credentials"]
        assert credentials is not None
        return [
            CredentialData.from_dict(cast(CredentialDataDataType, credential))
            for credential in credentials
        ]

    async def get_credentials_cached(self, user_id: int) -> list[CredentialData]:
        """Return cached data for all credentials assigned to a user."""
        result = await self._endpoint.async_send_command(
            "access_control.get_credentials_cached",
            userId=user_id,
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        credentials = result["credentials"]
        assert credentials is not None
        return [
            CredentialData.from_dict(cast(CredentialDataDataType, credential))
            for credential in credentials
        ]

    async def get_credentials_by_type(
        self, credential_type: UserCredentialType
    ) -> list[CredentialData]:
        """Return fresh data for all credentials of the given type."""
        result = await self._endpoint.async_send_command(
            "access_control.get_credentials_by_type",
            credentialType=credential_type,
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        credentials = result["credentials"]
        assert credentials is not None
        return [
            CredentialData.from_dict(cast(CredentialDataDataType, credential))
            for credential in credentials
        ]

    async def get_credentials_by_type_cached(
        self, credential_type: UserCredentialType
    ) -> list[CredentialData]:
        """Return cached data for all credentials of the given type."""
        result = await self._endpoint.async_send_command(
            "access_control.get_credentials_by_type_cached",
            credentialType=credential_type,
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        credentials = result["credentials"]
        assert credentials is not None
        return [
            CredentialData.from_dict(cast(CredentialDataDataType, credential))
            for credential in credentials
        ]

    async def get_all_credentials(self) -> list[CredentialData]:
        """Return fresh data for all credentials regardless of type or user."""
        result = await self._endpoint.async_send_command(
            "access_control.get_all_credentials",
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        credentials = result["credentials"]
        assert credentials is not None
        return [
            CredentialData.from_dict(cast(CredentialDataDataType, credential))
            for credential in credentials
        ]

    async def get_all_credentials_cached(self) -> list[CredentialData]:
        """Return cached data for all credentials regardless of type or user."""
        result = await self._endpoint.async_send_command(
            "access_control.get_all_credentials_cached",
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        credentials = result["credentials"]
        assert credentials is not None
        return [
            CredentialData.from_dict(cast(CredentialDataDataType, credential))
            for credential in credentials
        ]

    async def assign_credential(
        self,
        credential_type: UserCredentialType,
        credential_slot: int,
        destination_user_id: int,
    ) -> AssignCredentialResult:
        """Reassign an existing credential to a different user."""
        result = await self._endpoint.async_send_command(
            "access_control.assign_credential",
            credentialType=credential_type,
            credentialSlot=credential_slot,
            destinationUserId=destination_user_id,
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        return AssignCredentialResult(result["result"])

    async def set_credential(
        self,
        user_id: int,
        credential_type: UserCredentialType,
        credential_slot: int,
        data: str | bytes,
    ) -> SetCredentialResult:
        """Create or update an access-control credential."""
        result = await self._endpoint.async_send_command(
            "access_control.set_credential",
            userId=user_id,
            credentialType=credential_type,
            credentialSlot=credential_slot,
            data=serialize_credential_data(data),
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        return SetCredentialResult(result["result"])

    async def delete_credential(
        self,
        user_id: int,
        credential_type: UserCredentialType,
        credential_slot: int,
    ) -> SetCredentialResult:
        """Delete an access-control credential."""
        result = await self._endpoint.async_send_command(
            "access_control.delete_credential",
            userId=user_id,
            credentialType=credential_type,
            credentialSlot=credential_slot,
            require_schema=48,
            wait_for_result=True,
        )
        assert result is not None
        return SetCredentialResult(result["result"])

    async def start_credential_learn(
        self,
        user_id: int,
        credential_type: UserCredentialType,
        credential_slot: int,
        timeout: int | None = None,
    ) -> SupervisionResult | None:
        """Start learning mode for an access-control credential."""
        cmd_kwargs: dict[str, Any] = {}
        if timeout is not None:
            cmd_kwargs["timeout"] = timeout
        result = await self._endpoint.async_send_command(
            "access_control.start_credential_learn",
            userId=user_id,
            credentialType=credential_type,
            credentialSlot=credential_slot,
            require_schema=48,
            wait_for_result=None,
            **cmd_kwargs,
        )
        return parse_supervision_result(result)

    async def cancel_credential_learn(self) -> SupervisionResult | None:
        """Cancel any active credential learn operation."""
        result = await self._endpoint.async_send_command(
            "access_control.cancel_credential_learn",
            require_schema=48,
            wait_for_result=None,
        )
        return parse_supervision_result(result)

    async def get_admin_code(self) -> str | None:
        """Return the configured admin code for access control."""
        result = await self._endpoint.async_send_command(
            "access_control.get_admin_code",
            require_schema=48,
            wait_for_result=True,
        )
        assert result
        return cast(str | None, result.get("code"))

    async def set_admin_code(self, code: str) -> SupervisionResult | None:
        """Set the admin code for access control."""
        result = await self._endpoint.async_send_command(
            "access_control.set_admin_code",
            code=code,
            require_schema=48,
            wait_for_result=None,
        )
        return parse_supervision_result(result)
