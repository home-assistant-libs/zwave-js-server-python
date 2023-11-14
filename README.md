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

## Optional dependencies

`zwave-js-server-python` optionally supports `orjson` which can be installed with the `orjson` extra (e.g. `pip install zwave-js-server-python[orjson]`)
