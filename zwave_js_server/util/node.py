"""Utility functions for Z-Wave JS nodes."""
import json
from typing import Dict, Optional, Union

from ..const import CommandClass, ConfigurationValueType
from ..exceptions import InvalidNewValue, NotFoundError, SetValueFailed
from ..model.node import Node
from ..model.value import ConfigurationValue, Value, get_value_id


def _validate_and_transform_new_value(
    zwave_value: Value, new_value: Union[int, str]
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


def partial_param_bit_shift(property_key: int) -> int:
    """Get the number of bits to shift the value for a given property key."""
    # We can get the binary representation of the property key, reverse it,
    # and find the first 1
    return bin(property_key)[::-1].index("1")


async def async_bulk_set_partial_config_parameters(
    node: Node,
    new_value: Union[int, Dict[str, Union[int, str]]],
    property_: int,
) -> None:
    """Bulk set partial configuration values on this node."""
    config_values = node.get_configuration_values()
    property_values = [
        value for value in config_values.values() if value.property_ == property_
    ]
    if len(property_values) == 0:
        raise NotFoundError(
            f"Configuration parameter {property_} for node {node.node_id} not found"
        )

    # If new_value is a dictionary, we need to calculate the full value to send
    if isinstance(new_value, dict):
        temp_value = 0
        # For each property key provided, we multiply the partial value by the multiplication factor
        # and send them to get the number to send
        for property_key, partial_value in new_value.items():
            value_id = get_value_id(
                node, CommandClass.CONFIGURATION, property_, property_key=property_key
            )
            if value_id not in node.values:
                raise NotFoundError(
                    f"Bitmask {property_key} ({hex(property_key)}) not found for "
                    f"parameter {property_}"
                )
            zwave_value = node.values[value_id]
            partial_value = _validate_and_transform_new_value(
                zwave_value, partial_value
            )
            temp_value += partial_value << partial_param_bit_shift(property_key)

        # To set partial parameters in bulk, we also have to include cached values for
        # property keys that haven't been specified
        for property_value in property_values:
            if property_value.property_key not in new_value:
                temp_value += property_value.value << partial_param_bit_shift(
                    property_value.property_key
                )

        new_value = temp_value
    else:
        property_keys = sorted(
            [value.property_key for value in property_values], reverse=True
        )
        temp_value = new_value

        # Break down the bulk value into partial values and validate them against
        # each partial parameter's metadata
        for property_key in property_keys:
            multiplication_factor = 2 ** partial_param_bit_shift(property_key)
            partial_value = int(temp_value / multiplication_factor)
            temp_value = temp_value % multiplication_factor
            zwave_value = node.values[
                get_value_id(
                    node,
                    CommandClass.CONFIGURATION,
                    property_,
                    property_key=property_key,
                )
            ]
            _validate_and_transform_new_value(zwave_value, partial_value)

    if (
        await node.async_send_command(
            "set_value",
            valueId={
                "commandClass": CommandClass.CONFIGURATION.value,
                "property": property_,
            },
            value=new_value,
        )
        is False
    ):
        raise SetValueFailed(
            "Unable to set value, refer to "
            "https://zwave-js.github.io/node-zwave-js/#/api/node?id=setvalue for "
            "possible reasons"
        )


async def async_set_config_parameter(
    node: Node,
    new_value: Union[int, str],
    property_or_property_name: Union[int, str],
    property_key: Optional[Union[int, str]] = None,
) -> ConfigurationValue:
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
            value_id = zwave_value.value_id
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
    if await node.async_set_value(zwave_value, new_value) is False:
        raise SetValueFailed(
            "Unable to set value, refer to "
            "https://zwave-js.github.io/node-zwave-js/#/api/node?id=setvalue for "
            "possible reasons"
        )

    return zwave_value
