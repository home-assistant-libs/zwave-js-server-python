"""Z-Wave node."""
from typing import List


class Node:
    def __init__(self, data: dict) -> None:
        """Initialize a node."""
        self.data = data

    @property
    def node_id(self) -> int:
        """Return the node_id."""
        return self.data.get("nodeId")

    @property
    def index(self) -> int:
        """Return the index."""
        return self.data.get("index")

    @property
    def installer_icon(self) -> int:
        """Return the installer_icon."""
        return self.data.get("installerIcon")

    @property
    def user_icon(self) -> int:
        """Return the user_icon."""
        return self.data.get("userIcon")

    @property
    def status(self) -> int:
        """Return the status."""
        return self.data.get("status")

    @property
    def ready(self) -> bool:
        """Return the ready."""
        return self.data.get("ready")

    @property
    def device_class(self) -> dict:  # XXXXXX NEEDS CLASS
        """Return the device_class."""
        return self.data.get("deviceClass")

    @property
    def is_listening(self) -> bool:
        """Return the is_listening."""
        return self.data.get("isListening")

    @property
    def is_frequent_listening(self) -> bool:
        """Return the is_frequent_listening."""
        return self.data.get("isFrequentListening")

    @property
    def is_routing(self) -> bool:
        """Return the is_routing."""
        return self.data.get("isRouting")

    @property
    def max_baud_rate(self) -> int:
        """Return the max_baud_rate."""
        return self.data.get("maxBaudRate")

    @property
    def is_secure(self) -> bool:
        """Return the is_secure."""
        return self.data.get("isSecure")

    @property
    def version(self) -> int:
        """Return the version."""
        return self.data.get("version")

    @property
    def is_beaming(self) -> bool:
        """Return the is_beaming."""
        return self.data.get("isBeaming")

    @property
    def manufacturer_id(self) -> int:
        """Return the manufacturer_id."""
        return self.data.get("manufacturerId")

    @property
    def product_id(self) -> int:
        """Return the product_id."""
        return self.data.get("productId")

    @property
    def product_type(self) -> int:
        """Return the product_type."""
        return self.data.get("productType")

    @property
    def firmware_version(self) -> str:
        """Return the firmware_version."""
        return self.data.get("firmwareVersion")

    @property
    def zwave_plus_version(self) -> int:
        """Return the zwave_plus_version."""
        return self.data.get("zwavePlusVersion")

    @property
    def node_type(self) -> int:
        """Return the node_type."""
        return self.data.get("nodeType")

    @property
    def role_type(self) -> int:
        """Return the role_type."""
        return self.data.get("roleType")

    @property
    def name(self) -> str:
        """Return the name."""
        return self.data.get("name")

    @property
    def location(self) -> str:
        """Return the location."""
        return self.data.get("location")

    @property
    def device_config(self) -> dict:  # XXXXXX NEEDS CLASS
        """Return the device_config."""
        return self.data.get("deviceConfig")

    @property
    def label(self) -> str:
        """Return the label."""
        return self.data.get("label")

    @property
    def neighbors(self) -> List[int]:
        """Return the neighbors."""
        return self.data.get("neighbors")

    @property
    def endpoint_count_is_dynamic(self) -> bool:
        """Return the endpoint_count_is_dynamic."""
        return self.data.get("endpointCountIsDynamic")

    @property
    def endpoints_have_identical_capabilities(self) -> bool:
        """Return the endpoints_have_identical_capabilities."""
        return self.data.get('                "endpointsHaveIdenticalCapabilities')

    @property
    def individual_endpoint_count(self) -> int:
        """Return the individual_endpoint_count."""
        return self.data.get("individualEndpointCount")

    @property
    def aggregated_endpoint_count(self) -> int:
        """Return the aggregated_endpoint_count."""
        return self.data.get("aggregatedEndpointCount")

    @property
    def interview_attempts(self) -> int:
        """Return the interview_attempts."""
        return self.data.get("interviewAttempts")

    def receive_event(self, event: dict):
        """Receive an event."""
        if event["event"] == "value added":
            return

        if event["event"] == "value updated":
            return

        if event["event"] == "value removed":
            return

        if event["event"] == "metadata updated":
            return

        if event["event"] == "value notification":
            return

        if event["event"] == "notification":
            return

        if event["event"] == "interview failed":
            return

        if event["event"] == "firmware update progress":
            return

        if event["event"] == "firmware update finished":
            return

        if event["event"] == "wake up":
            return

        if event["event"] == "sleep":
            return

        if event["event"] == "dead":
            return

        if event["event"] == "alive":
            return

        if event["event"] == "interview completed":
            return

        if event["event"] == "ready":
            return

        # TODO decide what to do with unknown event
        print(f"Unhandled node event for node {self.node_id}: {event}")
