"""Constants for access control related command classes."""

from __future__ import annotations

from enum import IntEnum


class UserCredentialType(IntEnum):
    """Credential types supported by User Credential CC."""

    NONE = 0
    PIN_CODE = 1
    PASSWORD = 2
    RFID_CODE = 3
    BLE = 4
    NFC = 5
    UWB = 6
    EYE_BIOMETRIC = 7
    FACE_BIOMETRIC = 8
    FINGER_BIOMETRIC = 9
    HAND_BIOMETRIC = 10
    UNSPECIFIED_BIOMETRIC = 11
    DESFIRE = 12


class UserCredentialUserType(IntEnum):
    """User types supported by User Credential CC."""

    GENERAL = 0
    PROGRAMMING = 3
    NON_ACCESS = 4
    DURESS = 5
    DISPOSABLE = 6
    EXPIRING = 7
    REMOTE_ONLY = 9


class UserCredentialRule(IntEnum):
    """Credential rules supported by User Credential CC."""

    SINGLE = 1
    DUAL = 2
    TRIPLE = 3


class UserCredentialLearnStatus(IntEnum):
    """Credential learn statuses supported by User Credential CC."""

    STARTED = 0
    SUCCESS = 1
    ALREADY_IN_PROGRESS = 2
    ENDED_NOT_DUE_TO_TIMEOUT = 3
    TIMEOUT = 4
    STEP_RETRY = 5
    INVALID_ADD_OPERATION_TYPE = 254
    INVALID_MODIFY_OPERATION_TYPE = 255


class SetUserResult(IntEnum):
    """Result for set_user / delete_user / delete_all_users commands."""

    OK = 0
    ERROR_ADD_REJECTED_LOCATION_OCCUPIED = 1
    ERROR_MODIFY_REJECTED_LOCATION_EMPTY = 2
    ERROR_UNKNOWN = 255


class SetCredentialResult(IntEnum):
    """Result for set_credential / delete_credential commands."""

    OK = 0
    ERROR_ADD_REJECTED_LOCATION_OCCUPIED = 1
    ERROR_MODIFY_REJECTED_LOCATION_EMPTY = 2
    ERROR_DUPLICATE_CREDENTIAL = 3
    ERROR_MANUFACTURER_SECURITY_RULES = 4
    ERROR_DUPLICATE_ADMIN_PIN_CODE = 5
    ERROR_WRONG_USER_UNIQUE_IDENTIFIER = 6
    ERROR_UNKNOWN = 255


class AssignCredentialResult(IntEnum):
    """Result for assign_credential commands."""

    OK = 0
    ERROR_INVALID_CREDENTIAL = 1
    ERROR_INVALID_USER = 2
    ERROR_UNKNOWN = 255
