"""Manage the data."""
from . import controller, node as node_pkg


class ZWaveData:
    def __init__(self, state: dict):
        self.controller = controller.Controller.from_state(state["controller"])
        self.nodes = {}
        for node_state in state["nodes"]:
            node = node_pkg.Node.from_state(node_state)
            self.nodes[node.node_id] = node

    def receive_event(self, event: dict):
        """Receive an event."""
        if event["source"] == "controller":
            self.controller.receive_event(event)
            return

        if event["source"] == "driver":
            # TODO handle this?
            pass

        if event["source"] != "node":
            # TODO warn unhandled type?
            return

        node = self.nodes.get(event["nodeId"])

        if node is None:
            # TODO handle event for unknown node
            return

        node.receive_event(event)
