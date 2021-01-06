from typing import List


class Controller:
    def __init__(self, data: dict) -> None:
        """Initialize controller."""
        self.data = data

    @property
    def library_version(self) -> str:
        """Return library_version."""
        return self.data.get("libraryVersion")

    @property
    def controller_type(self) -> int:
        """Return controller_type."""
        return self.data.get("type")

    @property
    def home_id(self) -> int:
        """Return home_id."""
        return self.data.get("homeId")

    @property
    def own_node_id(self) -> int:
        """Return own_node_id."""
        return self.data.get("ownNodeId")

    @property
    def is_secondary(self) -> bool:
        """Return is_secondary."""
        return self.data.get("isSecondary")

    @property
    def is_using_home_id_from_other_network(self) -> bool:
        """Return is_using_home_id_from_other_network."""
        return self.data.get("isUsingHomeIdFromOtherNetwork")

    @property
    def is_SIS_present(self) -> bool:
        """Return is_SIS_present."""
        return self.data.get("isSISPresent")

    @property
    def was_real_primary(self) -> bool:
        """Return was_real_primary."""
        return self.data.get("wasRealPrimary")

    @property
    def is_static_update_controller(self) -> bool:
        """Return is_static_update_controller."""
        return self.data.get("isStaticUpdateController")

    @property
    def is_slave(self) -> bool:
        """Return is_slave."""
        return self.data.get("isSlave")

    @property
    def serial_api_version(self) -> str:
        """Return serial_api_version."""
        return self.data.get("serialApiVersion")

    @property
    def manufacturer_id(self) -> int:
        """Return manufacturer_id."""
        return self.data.get("manufacturerId")

    @property
    def product_type(self) -> int:
        """Return product_type."""
        return self.data.get("productType")

    @property
    def product_id(self) -> int:
        """Return product_id."""
        return self.data.get("productId")

    @property
    def supported_function_types(self) -> List[int]:
        """Return supported_function_types."""
        return self.data.get("supportedFunctionTypes")

    @property
    def suc_node_id(self) -> int:
        """Return suc_node_id."""
        return self.data.get("sucNodeId")

    @property
    def supports_timers(self) -> bool:
        """Return supports_timers."""
        return self.data.get("supportsTimers")

    def receive_event(self, event: dict):
        """Receive an event."""
        if event["event"] == "inclusion failed":
            return

        if event["event"] == "exclusion failed":
            return

        if event["event"] == "inclusion started":
            return

        if event["event"] == "exclusion started":
            return

        if event["event"] == "inclusion stopped":
            return

        if event["event"] == "exclusion stopped":
            return

        if event["event"] == "node added":
            return

        if event["event"] == "node removed":
            return

        if event["event"] == "heal network progress":
            return

        if event["event"] == "heal network done":
            return

        # TODO decide what to do with unknown event
        print(f"Unhandled node event for controller: {event}")
