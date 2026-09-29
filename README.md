# zwave-js-server-python

Python library for communicating with [zwave-js-server](https://github.com/zwave-js/zwave-js-server/). Goal for this library is to replicate the structure and the events of Z-Wave JS 1:1. So it has a `Driver`, `Controller` and `Node` classes.

## Setup development environment

To setup your development environment, run `scripts/setup`, which will install all requirements and set up pre-commit checks.

## Trying it out

```shell
python3 -m zwave_js_server ws://localhost:3000
```

Or get the version of the server

```shell
python3 -m zwave_js_server ws://localhost:3000 --server-version
```

Or dump the state. Optionally add `--event-timeout 5` if you want to listen 5 seconds extra for events.

```shell
python3 -m zwave_js_server ws://localhost:3000 --dump-state
```

## Sending commands

```python
try:
    result = await client.async_send_command({ "command": "start_listening" })
except zwave_js_server.client.FailedCommand as err:
    print("Command failed with", err.error_code)
```

## Access control

Schema 48 adds typed access-control helpers exposed via the `AccessControlAPI`
wrapper:

- `node.access_control`: shortcut for the root endpoint API.
- `endpoint.access_control`: API for a specific endpoint.
- Call `await endpoint.access_control.is_supported()` before using other
  methods.
- Credential payloads accept `str | bytes`; binary credentials are converted to
  the websocket Buffer transport shape internally.

## Endpoint groups

Schema 51 exposes the endpoint groups defined in a device's config file. They
semantically group the endpoints of a device, like the individual clamps of a
multi-clamp energy meter:

- `node.endpoint_groups`: dict of `EndpointGroup` by group ID, empty if the
  device config defines none.
- `EndpointGroup.endpoints`: the endpoints of the group that exist on the node.
  `EndpointGroup.endpoint_indices` also contains indices the node does not have.
- `EndpointGroup.is_main_device`: whether the group represents the device as a
  whole.
- `endpoint.endpoint_group` / `node.get_endpoint_group(index)`: the group an
  endpoint belongs to, or `None` if it is ungrouped.
