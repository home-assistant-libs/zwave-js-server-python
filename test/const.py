"""Constants for tests."""
INVALID_MESSAGE_MSG = {}
FAILED_COMMAND_MSG = {
    "type": "result",
    "success": False,
    "errorCode": "unknown_error",
    "messageId": "test",
}
FAILED_ZWAVE_COMMAND_MSG = {
    "type": "result",
    "success": False,
    "errorCode": "zwave_error",
    "messageId": "test",
    "zwaveErrorCode": 1,
    "zwaveErrorMessage": "test",
}
SUCCESS_MSG = {
    "type": "result",
    "success": True,
}
