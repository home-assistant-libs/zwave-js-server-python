from dataclasses import dataclass
from typing import List


@dataclass
class Controller:
    library_version: str
    controller_type: int
    home_id: int
    own_node_id: int
    is_secondary: bool
    is_using_home_id_from_other_network: bool
    is_SIS_present: bool
    was_real_primary: bool
    is_static_update_controller: bool
    is_slave: bool
    serial_api_version: str
    manufacturer_id: int
    product_type: int
    product_id: int
    supported_function_types: List[int]
    suc_node_id: int
    supports_timers: bool

    @classmethod
    def from_state(cls, data):
        return cls(
            library_version=data.get("libraryVersion"),
            controller_type=data.get("type"),
            home_id=data.get("homeId"),
            own_node_id=data.get("ownNodeId"),
            is_secondary=data.get("isSecondary"),
            is_using_home_id_from_other_network=data.get(
                "isUsingHomeIdFromOtherNetwork"
            ),
            is_SIS_present=data.get("isSISPresent"),
            was_real_primary=data.get("wasRealPrimary"),
            is_static_update_controller=data.get("isStaticUpdateController"),
            is_slave=data.get("isSlave"),
            serial_api_version=data.get("serialApiVersion"),
            manufacturer_id=data.get("manufacturerId"),
            product_type=data.get("productType"),
            product_id=data.get("productId"),
            supported_function_types=data.get("supportedFunctionTypes"),
            suc_node_id=data.get("sucNodeId"),
            supports_timers=data.get("supportsTimers"),
        )
