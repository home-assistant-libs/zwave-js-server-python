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
