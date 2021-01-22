# zwave-js-server-python

Python library for communicating with zwave-js-server. Goal for this library is to replicate the structure and the events of Z-Wave JS 1:1. So it has a `Driver`, `Controller` and `Node` classes.

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
