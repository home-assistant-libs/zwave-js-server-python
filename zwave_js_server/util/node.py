"""Utility functions for Z-Wave JS nodes."""
from __future__ import annotations

import logging
from typing import cast

from ..const import CommandClass, CommandStatus, ConfigurationValueType, SetValueStatus
from ..exceptions import (
    BulkSetConfigParameterFailed,
    InvalidNewValue,
    NotFoundError,
    SetValueFailed,
    ValueTypeError,
)
from ..model.node import Node
from ..model.value import (
    ConfigurationValue,
    SetConfigParameterResult,
    SetValueResult,
    get_value_id_str,
)

_LOGGER = logging.getLogger(__name__)


def dump_node_state(node: Node) -> dict:
    """Get state from a node."""
    return {
        **node.data,
        "values": {value_id: value.data for value_id, value in node.values.items()},
        "endpoints": {idx: endpoint.data for idx, endpoint in node.endpoints.items()},
    }


def partial_param_bit_shift(property_key: int) -> int:
    """Get the number of bits to shift the value for a given property key."""
    # We can get the binary representation of the property key, reverse it,
    # and find the first 1
    return bin(property_key)[::-1].index("1")


async def async_set_config_parameter(
    node: Node,
    new_value: int | str,
    property_or_property_name: int | str,
    property_key: int | str | None = None,
    endpoint: int = 0,
) -> tuple[ConfigurationValue, SetConfigParameterResult]:
    """Set a value for a config parameter on this node.

    new_value and property_ can be provided as labels, so we need to resolve them to
    the appropriate key
    """
    config_values = node.get_configuration_values()

    # If a property name is provided, we have to search for the correct value since
    # we can't use value ID
    if isinstance(property_or_property_name, str):
        try:
            zwave_value = next(
                config_value
                for config_value in config_values.values()
                if config_value.property_name == property_or_property_name
                and config_value.endpoint == endpoint
            )
        except StopIteration:
            raise NotFoundError(
                "Configuration parameter with parameter name "
                f"{property_or_property_name} on node {node} endpoint {endpoint} "
                "could not be found"
            ) from None
    else:
        value_id = get_value_id_str(
            node,
            CommandClass.CONFIGURATION,
            property_or_property_name,
            endpoint=endpoint,
            property_key=property_key,
        )

        if value_id not in config_values:
            raise NotFoundError(
                f"Configuration parameter with value ID {value_id} could not be "
                "found"
            ) from None
        zwave_value = config_values[value_id]

    new_value = _validate_and_transform_new_value(zwave_value, new_value)

    # Finally attempt to set the value and return the Value object if successful
    result = await node.async_set_value(zwave_value, new_value)
    if result and result.status not in (
        SetValueStatus.WORKING,
        SetValueStatus.SUCCESS,
        SetValueStatus.SUCCESS_UNSUPERVISED,
    ):
        raise SetValueFailed(str(result))

    status = (
        SetConfigParameterResult(CommandStatus.ACCEPTED, result)
        if result is not None
        else SetConfigParameterResult(CommandStatus.QUEUED)
    )

    return zwave_value, status


async def async_bulk_set_partial_config_parameters(
    node: Node,
    property_: int,
    new_value: int | dict[int | str, int | str],
    endpoint: int = 0,
) -> SetConfigParameterResult:
    """Bulk set partial configuration values on this node."""
    config_values = node.get_configuration_values()
    partial_param_values = {
        value_id: value
        for value_id, value in config_values.items()
        if value.property_ == property_
        and value.endpoint == endpoint
        and value.property_key is not None
    }

    if not partial_param_values:
        # If we find a value with this property_, we know this value isn't split
        # into partial params
        if (
            get_value_id_str(
                node, CommandClass.CONFIGURATION, property_, endpoint=endpoint
            )
            in config_values
        ):
            # If the new value is provided as a dict, we don't have enough information
            # to set the parameter.
            if isinstance(new_value, dict):
                raise ValueTypeError(
                    f"Configuration parameter {property_} for node {node.node_id} "
                    f"endpoint {endpoint} does not have partials"
                )
            # If the new value is provided as an int, we may as well try to set it
            # using the standard utility function
            _LOGGER.info(
                "Falling back to async_set_config_parameter because no partials "
                "were found"
            )
            _, cmd_status = await async_set_config_parameter(
                node, new_value, property_, endpoint=endpoint
            )
            return cmd_status

        # Otherwise if we can't find any values with this property, this config
        # parameter does not exist
        raise NotFoundError(
            f"Configuration parameter {property_} for node {node.node_id} endpoint "
            f"{endpoint} not found"
        )

    # If new_value is a dictionary, we need to calculate the full value to send
    if isinstance(new_value, dict):
        new_value = _get_int_from_partials_dict(
            node, partial_param_values, property_, new_value, endpoint=endpoint
        )
    else:
        _validate_raw_int(partial_param_values, new_value)

    cmd_response = await node.async_send_command(
        "set_value",
        valueId={
            "commandClass": CommandClass.CONFIGURATION.value,
            "endpoint": endpoint,
            "property": property_,
        },
        value=new_value,
        require_schema=29,
    )

    # If we didn't wait for a response, we assume the command has been queued
    if cmd_response is None:
        return SetConfigParameterResult(CommandStatus.QUEUED)

    result = SetValueResult(cmd_response["result"])

    if result.status not in (
        SetValueStatus.WORKING,
        SetValueStatus.SUCCESS,
        SetValueStatus.SUCCESS_UNSUPERVISED,
    ):
        raise SetValueFailed(str(result))

    return SetConfigParameterResult(CommandStatus.ACCEPTED, result)


def _validate_and_transform_new_value(
    zwave_value: ConfigurationValue, new_value: int | str
) -> int:
    """Validate a new value and return the integer value to set."""
    # If needed, convert a state label to its key. We know the state exists because
    # of the validation above.
    if isinstance(new_value, str):
        try:
            new_value = int(
                next(
                    key
                    for key, label in zwave_value.metadata.states.items()
                    if label == new_value
                )
            )
        except StopIteration:
            raise InvalidNewValue(
                f"State '{new_value}' not found for parameter {zwave_value.value_id}"
            ) from None

    if zwave_value.configuration_value_type == ConfigurationValueType.UNDEFINED:
        # We need to use the Configuration CC API to set the value for this type
        raise NotImplementedError("Configuration values of undefined type can't be set")

    return new_value


def _bulk_set_validate_and_transform_new_value(
    zwave_value: ConfigurationValue, property_key: int, new_partial_value: int | str
) -> int:
    """
    Validate and transform new value for a bulk set function call.

    Returns a bulk set friendly error if validation fails.
    """
    try:
        return _validate_and_transform_new_value(zwave_value, new_partial_value)
    except (InvalidNewValue, NotImplementedError) as err:
        raise BulkSetConfigParameterFailed(
            f"Config parameter {zwave_value.value_id} failed validation on partial "
            f"parameter {property_key}"
        ) from err


def _get_int_from_partials_dict(
    node: Node,
    partial_param_values: dict[str, ConfigurationValue],
    property_: int,
    new_value: dict[int | str, int | str],
    endpoint: int = 0,
) -> int:
    """Take an input dict for a set of partial values and compute the raw int value."""
    int_value = 0
    provided_partial_values = []
    # For each property key provided, we bit shift the partial value using the
    # property_key
    for property_key_or_name, partial_value in new_value.items():
        # If the dict key is a property key, we can generate the value ID to find the
        # partial value
        if isinstance(property_key_or_name, int):
            value_id = get_value_id_str(
                node,
                CommandClass.CONFIGURATION,
                property_,
                property_key=property_key_or_name,
                endpoint=endpoint,
            )
            if value_id not in partial_param_values:
                raise NotFoundError(
                    f"Bitmask {property_key_or_name} ({hex(property_key_or_name)}) "
                    f"not found for parameter {property_} on node {node} endpoint "
                    f"{endpoint}"
                )
            zwave_value = partial_param_values[value_id]
        # If the dict key is a property name, we have to find the value from the list
        # of partial param values
        else:
            try:
                zwave_value = next(
                    value
                    for value in partial_param_values.values()
                    if value.property_name == property_key_or_name
                    and value.endpoint == endpoint
                )
            except StopIteration:
                raise NotFoundError(
                    f"Partial parameter with label '{property_key_or_name}'"
                    f"not found for parameter {property_} on node {node} endpoint "
                    f"{endpoint}"
                ) from None

        provided_partial_values.append(zwave_value)
        property_key = cast(int, zwave_value.property_key)
        partial_value = _bulk_set_validate_and_transform_new_value(
            zwave_value, property_key, partial_value
        )
        int_value += partial_value << partial_param_bit_shift(property_key)

    # To set partial parameters in bulk, we also have to include cached values for
    # property keys that haven't been specified
    missing_values = set(partial_param_values.values()) - set(provided_partial_values)
    int_value += sum(
        cast(int, property_value.value)
        << partial_param_bit_shift(cast(int, property_value.property_key))
        for property_value in missing_values
    )

    return int_value


def _validate_raw_int(
    partial_param_values: dict[str, ConfigurationValue], new_value: int
) -> None:
    """
    Validate raw value against all partial values.

    Raises if a partial value in the raw value is invalid.
    """
    # Break down the bulk value into partial values and validate them against
    # each partial parameter's metadata by looping through the property values
    # starting with the highest property key
    for zwave_value in sorted(
        partial_param_values.values(),
        key=lambda val: cast(int, val.property_key),
        reverse=True,
    ):
        property_key = cast(int, zwave_value.property_key)
        multiplication_factor = 2 ** partial_param_bit_shift(property_key)
        partial_value = int(new_value / multiplication_factor)
        new_value = new_value % multiplication_factor
        _bulk_set_validate_and_transform_new_value(
            zwave_value, property_key, partial_value
        )
