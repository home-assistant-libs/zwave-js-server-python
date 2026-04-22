"""Constants for access control related command classes."""

from __future__ import annotations

from enum import IntEnum


class UserCredentialType(IntEnum):
    """Credential types supported by User Credential CC."""

    NONE = 0x00
    PIN_CODE = 0x01
    PASSWORD = 0x02
    RFID_CODE = 0x03
    BLE = 0x04
    NFC = 0x05
    UWB = 0x06
    EYE_BIOMETRIC = 0x07
    FACE_BIOMETRIC = 0x08
    FINGER_BIOMETRIC = 0x09
    HAND_BIOMETRIC = 0x0A
    UNSPECIFIED_BIOMETRIC = 0x0B
    DESFIRE = 0x0C


class UserCredentialUserType(IntEnum):
    """User types supported by User Credential CC."""

    GENERAL = 0x00
    PROGRAMMING = 0x03
    NON_ACCESS = 0x04
    DURESS = 0x05
    DISPOSABLE = 0x06
    EXPIRING = 0x07
    REMOTE_ONLY = 0x09


class UserCredentialRule(IntEnum):
    """Credential rules supported by User Credential CC."""

    SINGLE = 0x01
    DUAL = 0x02
    TRIPLE = 0x03


class UserCredentialLearnStatus(IntEnum):
    """Credential learn statuses supported by User Credential CC."""

    STARTED = 0x00
    SUCCESS = 0x01
    ALREADY_IN_PROGRESS = 0x02
    ENDED_NOT_DUE_TO_TIMEOUT = 0x03
    TIMEOUT = 0x04
    STEP_RETRY = 0x05
    INVALID_ADD_OPERATION_TYPE = 0xFE
    INVALID_MODIFY_OPERATION_TYPE = 0xFF


class SetUserResult(IntEnum):
    """Result for set_user / delete_user / delete_all_users commands."""

    OK = 0
    ERROR_ADD_REJECTED_LOCATION_OCCUPIED = 1
    ERROR_MODIFY_REJECTED_LOCATION_EMPTY = 2
    ERROR_UNKNOWN = 0xFF


class SetCredentialResult(IntEnum):
    """Result for set_credential / delete_credential commands."""

    OK = 0
    ERROR_ADD_REJECTED_LOCATION_OCCUPIED = 1
    ERROR_MODIFY_REJECTED_LOCATION_EMPTY = 2
    ERROR_DUPLICATE_CREDENTIAL = 3
    ERROR_MANUFACTURER_SECURITY_RULES = 4
    ERROR_DUPLICATE_ADMIN_PIN_CODE = 5
    ERROR_WRONG_USER_UNIQUE_IDENTIFIER = 6
    ERROR_UNKNOWN = 0xFF


class AssignCredentialResult(IntEnum):
    """Result for assign_credential commands."""

    OK = 0
    ERROR_INVALID_CREDENTIAL = 1
    ERROR_INVALID_USER = 2
    ERROR_UNKNOWN = 0xFF
