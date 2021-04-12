"""Utility functions for Z-Wave JS nodes."""
import json
import logging
from typing import Dict, Optional, Tuple, Union, cast

from ..const import CommandClass, CommandStatus, ConfigurationValueType
from ..exceptions import (
    BulkSetConfigParameterFailed,
    InvalidNewValue,
    NotFoundError,
    SetValueFailed,
    ValueTypeError,
)
from ..model.node import Node
from ..model.value import ConfigurationValue, get_value_id

_LOGGER = logging.getLogger(__name__)


def partial_param_bit_shift(property_key: int) -> int:
    """Get the number of bits to shift the value for a given property key."""
    # We can get the binary representation of the property key, reverse it,
    # and find the first 1
    return bin(property_key)[::-1].index("1")


async def async_set_config_parameter(
    node: Node,
    new_value: Union[int, str],
    property_or_property_name: Union[int, str],
    property_key: Optional[Union[int, str]] = None,
) -> Tuple[ConfigurationValue, CommandStatus]:
    """
    Set a value for a config parameter on this node.

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
            )
        except StopIteration:
            raise NotFoundError(
                "Configuration parameter with parameter name "
                f"{property_or_property_name} could not be found"
            ) from None
    else:
        value_id = get_value_id(
            node,
            CommandClass.CONFIGURATION,
            property_or_property_name,
            endpoint=0,
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
    success = await node.async_set_value(zwave_value, new_value)
    if success is False:
        raise SetValueFailed(
            "Unable to set value, refer to "
            "https://zwave-js.github.io/node-zwave-js/#/api/node?id=setvalue for "
            "possible reasons"
        )

    status = CommandStatus.ACCEPTED if success else CommandStatus.QUEUED

    return zwave_value, status


async def async_bulk_set_partial_config_parameters(
    node: Node,
    property_: int,
    new_value: Union[int, Dict[Union[int, str], Union[int, str]]],
) -> CommandStatus:
    """Bulk set partial configuration values on this node."""
    config_values = node.get_configuration_values()
    partial_param_values = {
        value_id: value
        for value_id, value in config_values.items()
        if value.property_ == property_ and value.property_key is not None
    }

    if not partial_param_values:
        # If we find a value with this property_, we know this value isn't split
        # into partial params
        if get_value_id(node, CommandClass.CONFIGURATION, property_) in config_values:
            # If the new value is provided as a dict, we don't have enough information
            # to set the parameter.
            if isinstance(new_value, dict):
                raise ValueTypeError(
                    f"Configuration parameter {property_} for node {node.node_id} "
                    "does not have partials"
                )
            # If the new value is provided as an int, we may as well try to set it
            # using the standard utility function
            _LOGGER.info(
                "Falling back to async_set_config_parameter because no partials "
                "were found"
            )
            _, cmd_status = await async_set_config_parameter(node, new_value, property_)
            return cmd_status

        # Otherwise if we can't find any values with this property, this config
        # parameter does not exist
        raise NotFoundError(
            f"Configuration parameter {property_} for node {node.node_id} not found"
        )

    # If new_value is a dictionary, we need to calculate the full value to send
    if isinstance(new_value, dict):
        new_value = _get_int_from_partials_dict(
            node, partial_param_values, property_, new_value
        )
    else:
        _validate_raw_int(partial_param_values, new_value)

    cmd_response = await node.async_send_command(
        "set_value",
        valueId={
            "commandClass": CommandClass.CONFIGURATION.value,
            "property": property_,
        },
        value=new_value,
    )

    # If we didn't wait for a response, we assume the command has been queued
    if cmd_response is None:
        return CommandStatus.QUEUED

    if not cast(bool, cmd_response["success"]):
        raise SetValueFailed(
            "Unable to set value, refer to "
            "https://zwave-js.github.io/node-zwave-js/#/api/node?id=setvalue for "
            "possible reasons"
        )

    # If we received a response that is not false, the command was successful
    return CommandStatus.ACCEPTED


def _validate_and_transform_new_value(
    zwave_value: ConfigurationValue, new_value: Union[int, str]
) -> int:
    """Validate a new value and return the integer value to set."""
    # Validate that new value for enumerated configuration parameter is a valid state
    # key or label
    if (
        zwave_value.configuration_value_type == ConfigurationValueType.ENUMERATED
        and str(new_value)
        not in [
            *zwave_value.metadata.states,
            *zwave_value.metadata.states.values(),
        ]
    ):
        raise InvalidNewValue(
            f"Must provide a value for {zwave_value.value_id} that represents a valid "
            f"state key or label from {json.dumps(zwave_value.metadata.states)}"
        )

    # Validate that new value for manual entry configuration parameter is a valid state
    # key or label
    if (
        isinstance(new_value, str)
        and zwave_value.configuration_value_type == ConfigurationValueType.MANUAL_ENTRY
        and str(new_value) not in zwave_value.metadata.states.values()
    ):
        raise InvalidNewValue(
            f"Must provide a value for {zwave_value.value_id} that represents a valid "
            f"state from {list(zwave_value.metadata.states.values())}"
        )

    # If needed, convert a state label to its key. We know the state exists because
    # of the validation above.
    if isinstance(new_value, str):
        new_value = int(
            next(
                key
                for key, label in zwave_value.metadata.states.items()
                if label == new_value
            )
        )

    if zwave_value.configuration_value_type == ConfigurationValueType.UNDEFINED:
        # We need to use the Configuration CC API to set the value for this type
        raise NotImplementedError("Configuration values of undefined type can't be set")

    # Validate that new value for range configuration parameter is within bounds
    max_ = zwave_value.metadata.max
    min_ = zwave_value.metadata.min
    check_ = (
        zwave_value.configuration_value_type == ConfigurationValueType.RANGE
        or zwave_value.configuration_value_type == ConfigurationValueType.MANUAL_ENTRY
    )
    if check_ and (
        (max_ is not None and new_value > max_)
        or (min_ is not None and new_value < min_)
    ):
        bounds = []
        if min_ is not None:
            bounds.append(f"Min: {min_}")
        if max_ is not None:
            bounds.append(f"Max: {max_}")
        raise InvalidNewValue(
            f"Must provide a value within the target range ({', '.join(bounds)})"
        )

    return new_value


def _bulk_set_validate_and_transform_new_value(
    zwave_value: ConfigurationValue,
    property_key: int,
    new_partial_value: Union[int, str],
) -> int:
    """
    Validate and transform new value for a bulk set function call.

    Returns a bulk set friendly error if validation fails.
    """
    try:
        return _validate_and_transform_new_value(zwave_value, new_partial_value)
    except (InvalidNewValue, NotImplementedError) as err:
        raise BulkSetConfigParameterFailed(
            f"Config parameter {zwave_value.property_} failed validation on partial "
            f"parameter {property_key}"
        ) from err


def _get_int_from_partials_dict(
    node: Node,
    partial_param_values: Dict[str, ConfigurationValue],
    property_: int,
    new_value: Dict[Union[int, str], Union[int, str]],
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
            value_id = get_value_id(
                node,
                CommandClass.CONFIGURATION,
                property_,
                property_key=property_key_or_name,
            )
            if value_id not in partial_param_values:
                raise NotFoundError(
                    f"Bitmask {property_key_or_name} ({hex(property_key_or_name)}) "
                    f"not found for parameter {property_}"
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
                )
            except StopIteration:
                raise NotFoundError(
                    f"Partial parameter with label '{property_key_or_name}'"
                    f"not found for parameter {property_}"
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
    partial_param_values: Dict[str, ConfigurationValue], new_value: int
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
