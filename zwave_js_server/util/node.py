"""Utility functions for Z-Wave JS nodes."""
import json
from typing import Optional, Union

from ..const import CommandClass, ConfigurationValueType
from ..exceptions import InvalidNewValue, NotFoundError, SetValueFailed
from ..model.node import Node
from ..model.value import ConfigurationValue, get_value_id


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

        try:
            zwave_value = config_values[value_id]
        except KeyError:
            raise NotFoundError(
                f"Configuration parameter with value ID {value_id} could not be "
                "found"
            ) from None

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
            "Must provide a value that represents a valid state key or label from "
            f"{json.dumps(zwave_value.metadata.states)}"
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
    if zwave_value.configuration_value_type == ConfigurationValueType.RANGE and (
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

    # Finally attempt to set the value and return the Value object if successful
    if not await node.async_set_value(zwave_value, new_value):
        raise SetValueFailed(
            "Unable to set value, refer to "
            "https://zwave-js.github.io/node-zwave-js/#/api/node?id=setvalue for "
            "possible reasons"
        )

    return zwave_value
