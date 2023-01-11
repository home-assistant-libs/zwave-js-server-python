# Scripts

This directory contains scripts that are used to help maintain this library.

To run these scripts, you will need to install `zwave-js-server-python` library's [requirements_scripts.txt](../../requirements_scripts.txt) into your environment.

These scripts have to be run manually, and any changes that result from running the scripts have to be submitted as a PR to be included in the project.

## `generate_multilevel_sensor_constants.py`

This script is used to download the latest multilevel sensor types and scales JSON files from the [zwave-js](https://github.com/zwave-js/zwave-js-server) repository and generate constants for the multilevel sensor command class. The generated constants can be found [here](../../zwave_js_server/const/command_class/multilevel_sensor.py).

## `run_mock_server.py`

This script allows you to run a mock Z-Wave JS Server instance using a network state dump from the `zwave-js-server-python` library. While the functionality is limited for now and is intended to be expanded in the future, the mock server also supports manipulating the state of the network by replaying events on it and emulating a responsive network by setting up mocked responses to commands. The main purpose of this mock server is to allow developers to test, build, and troubleshoot applications that use the `zwave-js-server-python` library to integrate with [zwave-js](https://github.com/zwave-js/node-zwave-js) (e.g. Home Assistant).

### Usage

At a minimum, the mock server instance needs the file path to a network state dump (which can be retrieved from an existing network using the library's [dump](../../zwave_js_server/dump.py) module). All other inputs are optional.

```
usage: run_mock_server.py [-h] [--host HOST] [--port PORT] [--log-level {DEBUG,INFO,WARNING,ERROR}] [--events-to-replay-path EVENTS_TO_REPLAY_PATH]
                          [--command-results-path COMMAND_RESULTS_PATH] [--combined-replay-dump-path COMBINED_REPLAY_DUMP_PATH]
                          network_state_path

Mock Z-Wave JS Server

positional arguments:
  network_state_path    File path to network state dump JSON.

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Host to bind to
  --port PORT           Port to run on (defaults to 3000)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Log level for the mock server instance
  --events-to-replay-path EVENTS_TO_REPLAY_PATH
                        File path to events to replay JSON. Events provided by --combined-replay-dump-path option will be first, followed by events from this
                        file.
  --command-results-path COMMAND_RESULTS_PATH
                        File path to command result JSON. Command results provided by --combined-replay-dump-path option will be first, followed by results
                        from this file.
  --combined-replay-dump-path COMBINED_REPLAY_DUMP_PATH
                        File path to the combined event and command result dump JSON. Events and command results will be extracted in the order they were
                        received.
```

### Inputs/File Formats

#### Network State Dump (required)

The network state dump tells the server what the initial state of the network should be for the driver, the controller, and all of the network's nodes. The output of the library's [dump](../../zwave_js_server/dump.py) module can be used directly as the input to the server.

##### File Format

```json
[
    {
        "type": "version",
        "driverVersion": "10.3.1",
        "serverVersion": "1.24.1",
        "homeId": "123456789",
        "minSchemaVersion": 0,
        "maxSchemaVersion": 24
    },
    {
        "type": "result",
        "success": true,
        "messageId": "initialize",
        "result": {}
    },
    {
        "type": "result",
        "success": true,
        "messageId": "start-listening",
        "result": {
            "state": {
                "driver": {
                    ... // driver state dictionary
                },
                "controller": {
                    ... // controller state dictinoary
                },
                "nodes": [
                    ... // list of node state dictionaries
                ]
            }
        }
    }
]
```

#### Events to Replay (optional)

`zwave-js` events can be replayed on the server once a client has connected to the server instance and started listening to emulate things happening on the network. These events can be provided initially at runtime via a JSON file, but the server also has an endpoint `/replay` that can be POSTed to in order to add events to the replay queue.

Command results can be recorded from a live network using the library's Client class (see the Recording section)

##### Limitations

- The queue currently only gets played immediately after a new client starts listening to the server
- The events will fire sequentially without any delays between the events
- There is currently no way to clear the queue
- There is currently no way to fire an event on demand
- There is currently no way to control the timing of the events
- There is currently no way to reorder events in the queue

##### File Format

```json
[
    {
        "record_type": "event",
        "ts": "2017-02-15T20:26:08.937881", // unused, can be omitted
        "type": "<zwave-js event name>", // unused, can be omitted
        "event_msg": {
            ... // event message as the server would send it to the client
        }
    }
]
```

#### Command Results (optional)

The server can respond to commands from a queue of command responses. After each command, the first response for that command is removed from the queue and sent back to the client. In this way, you can control the exact behavior of what the server would send the client, even if there are multiple calls for the same command. These command results can be provided initially at runtime via a JSON file, but the server also has an endpoint `/replay` that can be POSTed to in order to add command results to the queue.

Command results can be recorded from a live network using the library's Client class (see the Recording section)

##### Limitations

- Unlike events, which remain in the queue forever, command results are only returned once. To add to the queue, use the `/replay` endpoint
- There is currently no way to clear a queue for a particular command
- There is currently no way to clear all command responses
- There is currently no way to reorder command results in the queue

##### File Format

```json
[
    {
        "record_type": "command",
        "ts": "2017-02-15T20:26:08.937881", // unused, can be omitted
        "command": "<zwave-js-server command name>", // unused, can be omitted
        "command_msg": {
            ... // command message as the library would send it to the server
        },
        "result_ts": "2017-02-15T20:26:08.937881", // unused, can be omitted
        "result_msg": {
            ... // response message as the server would send it to the client
        }
    }
]
```

### Recording events and commands/command responses

The library's Client class can record event and command/command result messages that occur between a server instance and a client. This would allow you to e.g. troubleshoot a user's problem by having them record everything that happens, reproduce the issue, and then send you the result to feed directly into the mock server.

#### Begin recording

There are two ways to enable recording of commands and messages:
1. When creating the Client class instance, pass `record_messages=True` into the Client constructor and the class instance will begin recording all events, commands, and results of commands after the client starts listening to updates from the server.
2. Call `Client.begin_recording_messages()` at any point to begin recording all events, commands, and results of commands.

#### End recording

You can end recording by calling `Client.end_recording_messages()`. This call will return a list which can be directly passed into the `--combined-replay-dump-path` option once serialized to a JSON file.

### `/replay` endpoint

The `replay` endpoint accepts an HTTP POST request with either a single event or command/command response or a list of them. They will be added to the end of their respective queue.
