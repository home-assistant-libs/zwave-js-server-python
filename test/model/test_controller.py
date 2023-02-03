"""Test the controller model."""
import json
from copy import deepcopy
from unittest.mock import patch

import pytest

from zwave_js_server.const import (
    ExclusionStrategy,
    InclusionState,
    InclusionStrategy,
    NodeType,
    ProtocolDataRate,
    Protocols,
    ProvisioningEntryStatus,
    QRCodeVersion,
    RFRegion,
    SecurityClass,
    ZwaveFeature,
)
from zwave_js_server.event import Event
from zwave_js_server.exceptions import RepeaterRssiErrorReceived, RssiErrorReceived
from zwave_js_server.model import association as association_pkg
from zwave_js_server.model import controller as controller_pkg
from zwave_js_server.model.controller.firmware import ControllerFirmwareUpdateStatus
from zwave_js_server.model.controller.statistics import ControllerStatistics
from zwave_js_server.model.node import Node
from zwave_js_server.model.node.firmware import NodeFirmwareUpdateFileInfo

from .. import load_fixture


def test_from_state():
    """Test from_state method."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["result"]["state"]

    ctrl = controller_pkg.Controller(None, state)

    assert ctrl.sdk_version == "Z-Wave 3.95"
    assert ctrl.controller_type == 1
    assert ctrl.home_id == 3601639587
    assert ctrl.own_node_id == 1
    assert isinstance(ctrl.own_node, Node)
    assert ctrl.is_primary
    assert ctrl.is_using_home_id_from_other_network is False
    assert ctrl.is_SIS_present is True
    assert ctrl.was_real_primary is True
    assert ctrl.is_suc is True
    assert ctrl.node_type == NodeType.CONTROLLER
    assert ctrl.firmware_version == "1.0"
    assert ctrl.manufacturer_id == 134
    assert ctrl.product_type == 257
    assert ctrl.product_id == 90
    assert ctrl.supported_function_types == [
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        28,
        32,
        33,
        34,
        35,
        36,
        39,
        41,
        42,
        43,
        44,
        45,
        65,
        66,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        80,
        81,
        83,
        84,
        85,
        86,
        87,
        94,
        96,
        97,
        98,
        99,
        102,
        103,
        128,
        144,
        146,
        147,
        152,
        180,
        182,
        183,
        184,
        185,
        186,
        189,
        190,
        191,
        210,
        211,
        212,
        238,
        239,
    ]
    assert ctrl.suc_node_id == 1
    assert ctrl.supports_timers is False
    assert ctrl.is_heal_network_active is False
    assert ctrl.inclusion_state == InclusionState.IDLE
    stats = ctrl.statistics
    assert (
        stats.can
        == stats.messages_dropped_rx
        == stats.messages_dropped_tx
        == stats.messages_rx
        == stats.messages_tx
        == stats.nak
        == stats.timeout_ack
        == stats.timeout_callback
        == stats.timeout_response
        == 0
    )
    assert ctrl.rf_region is None


def test_controller_mods():
    """Test modifications to controller method."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["result"]["state"]
    state["controller"].pop("ownNodeId")
    state["controller"]["rfRegion"] = 0

    ctrl = controller_pkg.Controller(None, state)
    assert ctrl.own_node_id is None
    assert ctrl.own_node is None
    assert ctrl.rf_region == RFRegion.EUROPE


async def test_begin_inclusion(controller, uuid4, mock_command):
    """Test begin inclusion."""
    ack_commands = mock_command(
        {"command": "controller.begin_inclusion"},
        {"success": True},
    )
    assert await controller.async_begin_inclusion(InclusionStrategy.SECURITY_S0)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_inclusion",
        "options": {"strategy": InclusionStrategy.SECURITY_S0},
        "messageId": uuid4,
    }


async def test_begin_inclusion_default(controller, uuid4, mock_command):
    """Test begin inclusion."""
    ack_commands = mock_command(
        {"command": "controller.begin_inclusion"},
        {"success": True},
    )
    assert await controller.async_begin_inclusion(InclusionStrategy.DEFAULT)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_inclusion",
        "options": {
            "strategy": InclusionStrategy.DEFAULT,
        },
        "messageId": uuid4,
    }


async def test_begin_inclusion_default_force_security(controller, uuid4, mock_command):
    """Test begin inclusion with force_security provided."""
    ack_commands = mock_command(
        {"command": "controller.begin_inclusion"},
        {"success": True},
    )
    assert await controller.async_begin_inclusion(
        InclusionStrategy.DEFAULT, force_security=False
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_inclusion",
        "options": {
            "strategy": InclusionStrategy.DEFAULT,
            "forceSecurity": False,
        },
        "messageId": uuid4,
    }


async def test_begin_inclusion_s2_no_input(controller, uuid4, mock_command):
    """Test begin inclusion S2 Mode."""
    ack_commands = mock_command(
        {"command": "controller.begin_inclusion"},
        {"success": True},
    )
    assert await controller.async_begin_inclusion(InclusionStrategy.SECURITY_S2)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_inclusion",
        "options": {"strategy": InclusionStrategy.SECURITY_S2},
        "messageId": uuid4,
    }


async def test_begin_inclusion_s2_qr_code_string(controller, uuid4, mock_command):
    """Test begin inclusion S2 Mode with a QR code string."""
    ack_commands = mock_command(
        {"command": "controller.begin_inclusion"},
        {"success": True},
    )
    assert await controller.async_begin_inclusion(
        InclusionStrategy.SECURITY_S2,
        provisioning="90testtesttesttesttesttesttesttesttesttesttesttesttest",
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_inclusion",
        "options": {
            "strategy": InclusionStrategy.SECURITY_S2,
            "provisioning": "90testtesttesttesttesttesttesttesttesttesttesttesttest",
        },
        "messageId": uuid4,
    }

    # Test invalid QR code length fails
    with pytest.raises(ValueError):
        await controller.async_begin_inclusion(
            InclusionStrategy.SECURITY_S2,
            provisioning="test",
        )


async def test_begin_inclusion_s2_provisioning_entry(controller, uuid4, mock_command):
    """Test begin inclusion S2 Mode with a provisioning entry."""
    ack_commands = mock_command(
        {"command": "controller.begin_inclusion"},
        {"success": True},
    )
    provisioning_entry = controller_pkg.ProvisioningEntry(
        "test",
        [SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        additional_properties={"test": "test"},
    )
    assert await controller.async_begin_inclusion(
        InclusionStrategy.SECURITY_S2, provisioning=provisioning_entry
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_inclusion",
        "options": {
            "strategy": InclusionStrategy.SECURITY_S2,
            "provisioning": {
                "dsk": "test",
                "securityClasses": [0],
                "requestedSecurityClasses": [0],
                "status": 0,
                "test": "test",
            },
        },
        "messageId": uuid4,
    }


async def test_begin_inclusion_s2_qr_info(controller, uuid4, mock_command):
    """Test begin inclusion S2 Mode with QR info."""
    ack_commands = mock_command(
        {"command": "controller.begin_inclusion"},
        {"success": True},
    )
    provisioning_entry = controller_pkg.QRProvisioningInformation(
        dsk="test1",
        security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        status=ProvisioningEntryStatus.INACTIVE,
        version=QRCodeVersion.S2,
        generic_device_class=1,
        specific_device_class=2,
        installer_icon_type=3,
        manufacturer_id=4,
        product_type=5,
        product_id=6,
        application_version="test2",
        max_inclusion_request_interval=7,
        uuid="test3",
        supported_protocols=None,
    )
    assert await controller.async_begin_inclusion(
        InclusionStrategy.SECURITY_S2, provisioning=provisioning_entry
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_inclusion",
        "options": {
            "strategy": InclusionStrategy.SECURITY_S2,
            "provisioning": {
                "version": 0,
                "securityClasses": [0],
                "requestedSecurityClasses": [0],
                "status": 1,
                "dsk": "test1",
                "genericDeviceClass": 1,
                "specificDeviceClass": 2,
                "installerIconType": 3,
                "manufacturerId": 4,
                "productType": 5,
                "productId": 6,
                "applicationVersion": "test2",
                "maxInclusionRequestInterval": 7,
                "uuid": "test3",
            },
        },
        "messageId": uuid4,
    }


async def test_begin_inclusion_errors(controller, uuid4, mock_command):
    """Test begin inclusion error scenarios."""
    provisioning_entry = controller_pkg.ProvisioningEntry(
        "test",
        [SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        additional_properties={"test": "test"},
    )
    # Test that Security S0 Inclusion Strategy doesn't support providing a provisioning
    # entry
    with pytest.raises(ValueError):
        await controller.async_begin_inclusion(
            InclusionStrategy.SECURITY_S0, provisioning=provisioning_entry
        )
    # Test that Security S2 Inclusion Strategy doesn't support providing `force_security`
    with pytest.raises(ValueError):
        await controller.async_begin_inclusion(
            InclusionStrategy.SECURITY_S2, force_security=True
        )

    # Test that Smart Start QR code can't be used async_begin_inclusion
    provisioning_entry = controller_pkg.QRProvisioningInformation(
        dsk="test1",
        security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        version=QRCodeVersion.SMART_START,
        generic_device_class=1,
        specific_device_class=2,
        installer_icon_type=3,
        manufacturer_id=4,
        product_type=5,
        product_id=6,
        application_version="test2",
        max_inclusion_request_interval=7,
        uuid="test3",
        supported_protocols=[Protocols.ZWAVE],
    )
    with pytest.raises(ValueError):
        await controller.async_begin_inclusion(
            InclusionStrategy.SECURITY_S2, provisioning=provisioning_entry
        )


async def test_provision_smart_start_node_qr_code_string(
    controller, uuid4, mock_command
):
    """Test provision smart start node with a QR code string."""
    ack_commands = mock_command(
        {"command": "controller.provision_smart_start_node"},
        {"success": True},
    )
    await controller.async_provision_smart_start_node("test")

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.provision_smart_start_node",
        "entry": "test",
        "messageId": uuid4,
    }


async def test_provision_smart_start_node_provisioning_entry(
    controller, uuid4, mock_command
):
    """Test provision smart start node with a provisioning entry."""
    ack_commands = mock_command(
        {"command": "controller.provision_smart_start_node"},
        {"success": True},
    )
    provisioning_entry = controller_pkg.ProvisioningEntry(
        "test",
        [SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        additional_properties={"test": "test"},
    )
    await controller.async_provision_smart_start_node(provisioning_entry)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.provision_smart_start_node",
        "entry": {
            "dsk": "test",
            "securityClasses": [0],
            "requestedSecurityClasses": [0],
            "status": 0,
            "test": "test",
        },
        "messageId": uuid4,
    }


async def test_provision_smart_start_node_qr_info(controller, uuid4, mock_command):
    """Test provision smart start with QR info."""
    ack_commands = mock_command(
        {"command": "controller.provision_smart_start_node"},
        {"success": True},
    )
    provisioning_entry = controller_pkg.QRProvisioningInformation(
        dsk="test1",
        security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        status=ProvisioningEntryStatus.INACTIVE,
        version=QRCodeVersion.SMART_START,
        generic_device_class=1,
        specific_device_class=2,
        installer_icon_type=3,
        manufacturer_id=4,
        product_type=5,
        product_id=6,
        application_version="test2",
        max_inclusion_request_interval=7,
        uuid="test3",
        supported_protocols=[Protocols.ZWAVE],
    )
    await controller.async_provision_smart_start_node(provisioning_entry)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.provision_smart_start_node",
        "entry": {
            "version": 1,
            "securityClasses": [0],
            "requestedSecurityClasses": [0],
            "status": 1,
            "dsk": "test1",
            "genericDeviceClass": 1,
            "specificDeviceClass": 2,
            "installerIconType": 3,
            "manufacturerId": 4,
            "productType": 5,
            "productId": 6,
            "applicationVersion": "test2",
            "maxInclusionRequestInterval": 7,
            "uuid": "test3",
            "supportedProtocols": [0],
        },
        "messageId": uuid4,
    }

    # Test that S2 QR Code can't be used with `async_provision_smart_start_node`
    provisioning_entry = controller_pkg.QRProvisioningInformation(
        dsk="test1",
        security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        version=QRCodeVersion.S2,
        generic_device_class=1,
        specific_device_class=2,
        installer_icon_type=3,
        manufacturer_id=4,
        product_type=5,
        product_id=6,
        application_version="test2",
        max_inclusion_request_interval=7,
        uuid="test3",
        supported_protocols=[Protocols.ZWAVE],
    )
    with pytest.raises(ValueError):
        await controller.async_provision_smart_start_node(provisioning_entry)


async def test_unprovision_smart_start_node(controller, uuid4, mock_command):
    """Test unprovision smart start node."""
    ack_commands = mock_command(
        {"command": "controller.unprovision_smart_start_node"},
        {"success": True},
    )
    await controller.async_unprovision_smart_start_node("test")

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.unprovision_smart_start_node",
        "dskOrNodeId": "test",
        "messageId": uuid4,
    }


async def test_get_provisioning_entry(controller, uuid4, mock_command):
    """Test get_provisioning_entry."""
    ack_commands = mock_command(
        {"command": "controller.get_provisioning_entry"},
        {
            "entry": {
                "dsk": "test",
                "securityClasses": [0],
                "requestedSecurityClasses": [0],
                "test": "test",
                "status": 0,
            }
        },
    )
    provisioning_entry = await controller.async_get_provisioning_entry("test")
    assert provisioning_entry == controller_pkg.ProvisioningEntry(
        "test",
        [SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        status=ProvisioningEntryStatus.ACTIVE,
        additional_properties={"test": "test"},
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_provisioning_entry",
        "dskOrNodeId": "test",
        "messageId": uuid4,
    }


async def test_get_provisioning_entry_undefined(controller, uuid4, mock_command):
    """Test get_provisioning_entry when entry is undefined."""
    ack_commands = mock_command(
        {"command": "controller.get_provisioning_entry"},
        {},
    )
    assert await controller.async_get_provisioning_entry("test") is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_provisioning_entry",
        "dskOrNodeId": "test",
        "messageId": uuid4,
    }


async def test_get_provisioning_entries(controller, uuid4, mock_command):
    """Test get_provisioning_entries."""
    ack_commands = mock_command(
        {"command": "controller.get_provisioning_entries"},
        {
            "entries": [
                {
                    "dsk": "test",
                    "securityClasses": [0],
                    "requestedSecurityClasses": [0],
                    "test": "test",
                    "status": 0,
                }
            ]
        },
    )
    provisioning_entry = await controller.async_get_provisioning_entries()
    assert provisioning_entry == [
        controller_pkg.ProvisioningEntry(
            "test",
            [SecurityClass.S2_UNAUTHENTICATED],
            status=ProvisioningEntryStatus.ACTIVE,
            requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
            additional_properties={"test": "test"},
        )
    ]

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_provisioning_entries",
        "messageId": uuid4,
    }


async def test_stop_inclusion(controller, uuid4, mock_command):
    """Test stop inclusion."""
    ack_commands = mock_command(
        {"command": "controller.stop_inclusion"},
        {"success": True},
    )
    assert await controller.async_stop_inclusion()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_inclusion",
        "messageId": uuid4,
    }


async def test_begin_exclusion(controller, uuid4, mock_command):
    """Test begin exclusion."""
    ack_commands = mock_command(
        {"command": "controller.begin_exclusion"},
        {"success": True},
    )
    assert await controller.async_begin_exclusion()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_exclusion",
        "messageId": uuid4,
    }


async def test_begin_exclusion_unprovision(controller, uuid4, mock_command):
    """Test begin exclusion with unprovision set."""
    ack_commands = mock_command(
        {"command": "controller.begin_exclusion"},
        {"success": True},
    )
    assert await controller.async_begin_exclusion(ExclusionStrategy.EXCLUDE_ONLY)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_exclusion",
        "strategy": ExclusionStrategy.EXCLUDE_ONLY,
        "messageId": uuid4,
    }


async def test_stop_exclusion(controller, uuid4, mock_command):
    """Test stop exclusion."""
    ack_commands = mock_command(
        {"command": "controller.stop_exclusion"},
        {"success": True},
    )
    assert await controller.async_stop_exclusion()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_exclusion",
        "messageId": uuid4,
    }


async def test_hash(controller):
    """Test node hash."""
    assert hash(controller) == hash(controller.home_id)


async def test_remove_failed_node(controller, multisensor_6, uuid4, mock_command):
    """Test remove failed node."""
    ack_commands = mock_command(
        {"command": "controller.remove_failed_node"},
        {},
    )

    assert await controller.async_remove_failed_node(multisensor_6) is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.remove_failed_node",
        "messageId": uuid4,
        "nodeId": multisensor_6.node_id,
    }


async def test_replace_failed_node(controller, multisensor_6, uuid4, mock_command):
    """Test replace_failed_node."""
    ack_commands = mock_command(
        {"command": "controller.replace_failed_node"},
        {"success": True},
    )
    assert await controller.async_replace_failed_node(
        multisensor_6, InclusionStrategy.SECURITY_S0
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.replace_failed_node",
        "nodeId": multisensor_6.node_id,
        "options": {"strategy": InclusionStrategy.SECURITY_S0},
        "messageId": uuid4,
    }


async def test_replace_failed_node_default(
    controller, multisensor_6, uuid4, mock_command
):
    """Test replace_failed_node."""
    ack_commands = mock_command(
        {"command": "controller.replace_failed_node"},
        {"success": True},
    )
    assert await controller.async_replace_failed_node(
        multisensor_6, InclusionStrategy.DEFAULT
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.replace_failed_node",
        "nodeId": multisensor_6.node_id,
        "options": {
            "strategy": InclusionStrategy.DEFAULT,
        },
        "messageId": uuid4,
    }


async def test_replace_failed_node_default_force_security(
    controller, multisensor_6, uuid4, mock_command
):
    """Test replace_failed_node with force_security provided."""
    ack_commands = mock_command(
        {"command": "controller.replace_failed_node"},
        {"success": True},
    )
    assert await controller.async_replace_failed_node(
        multisensor_6, InclusionStrategy.DEFAULT, force_security=False
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.replace_failed_node",
        "nodeId": multisensor_6.node_id,
        "options": {
            "strategy": InclusionStrategy.DEFAULT,
            "forceSecurity": False,
        },
        "messageId": uuid4,
    }


async def test_replace_failed_node_s2_no_input(
    controller, multisensor_6, uuid4, mock_command
):
    """Test replace_failed_node S2 Mode."""
    ack_commands = mock_command(
        {"command": "controller.replace_failed_node"},
        {"success": True},
    )
    assert await controller.async_replace_failed_node(
        multisensor_6, InclusionStrategy.SECURITY_S2
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.replace_failed_node",
        "nodeId": multisensor_6.node_id,
        "options": {"strategy": InclusionStrategy.SECURITY_S2},
        "messageId": uuid4,
    }


async def test_replace_failed_node_s2_qr_code_string(
    controller, multisensor_6, uuid4, mock_command
):
    """Test replace_failed_node S2 Mode with a QR code string."""
    ack_commands = mock_command(
        {"command": "controller.replace_failed_node"},
        {"success": True},
    )
    assert await controller.async_replace_failed_node(
        multisensor_6,
        InclusionStrategy.SECURITY_S2,
        provisioning="90testtesttesttesttesttesttesttesttesttesttesttesttest",
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.replace_failed_node",
        "nodeId": multisensor_6.node_id,
        "options": {
            "strategy": InclusionStrategy.SECURITY_S2,
            "provisioning": "90testtesttesttesttesttesttesttesttesttesttesttesttest",
        },
        "messageId": uuid4,
    }

    # Test invalid QR code length fails
    with pytest.raises(ValueError):
        await controller.async_replace_failed_node(
            multisensor_6,
            InclusionStrategy.SECURITY_S2,
            provisioning="test",
        )


async def test_replace_failed_node_s2_provisioning_entry(
    controller, multisensor_6, uuid4, mock_command
):
    """Test replace_failed_node S2 Mode with a provisioning entry."""
    ack_commands = mock_command(
        {"command": "controller.replace_failed_node"},
        {"success": True},
    )
    provisioning_entry = controller_pkg.ProvisioningEntry(
        "test",
        [SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        additional_properties={"test": "test"},
    )
    assert await controller.async_replace_failed_node(
        multisensor_6, InclusionStrategy.SECURITY_S2, provisioning=provisioning_entry
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.replace_failed_node",
        "nodeId": multisensor_6.node_id,
        "options": {
            "strategy": InclusionStrategy.SECURITY_S2,
            "provisioning": {
                "dsk": "test",
                "securityClasses": [0],
                "requestedSecurityClasses": [0],
                "status": 0,
                "test": "test",
            },
        },
        "messageId": uuid4,
    }


async def test_replace_failed_node_s2_qr_info(
    controller, multisensor_6, uuid4, mock_command
):
    """Test replace_failed_node S2 Mode with QR info."""
    ack_commands = mock_command(
        {"command": "controller.replace_failed_node"},
        {"success": True},
    )
    provisioning_entry = controller_pkg.QRProvisioningInformation(
        dsk="test1",
        security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        status=ProvisioningEntryStatus.INACTIVE,
        version=QRCodeVersion.S2,
        generic_device_class=1,
        specific_device_class=2,
        installer_icon_type=3,
        manufacturer_id=4,
        product_type=5,
        product_id=6,
        application_version="test2",
        max_inclusion_request_interval=7,
        uuid="test3",
        supported_protocols=None,
    )
    assert await controller.async_replace_failed_node(
        multisensor_6, InclusionStrategy.SECURITY_S2, provisioning=provisioning_entry
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.replace_failed_node",
        "nodeId": multisensor_6.node_id,
        "options": {
            "strategy": InclusionStrategy.SECURITY_S2,
            "provisioning": {
                "version": 0,
                "securityClasses": [0],
                "requestedSecurityClasses": [0],
                "status": 1,
                "dsk": "test1",
                "genericDeviceClass": 1,
                "specificDeviceClass": 2,
                "installerIconType": 3,
                "manufacturerId": 4,
                "productType": 5,
                "productId": 6,
                "applicationVersion": "test2",
                "maxInclusionRequestInterval": 7,
                "uuid": "test3",
            },
        },
        "messageId": uuid4,
    }


async def test_replace_failed_node_errors(controller, multisensor_6):
    """Test replace_failed_node error scenarios."""
    provisioning_entry = controller_pkg.ProvisioningEntry(
        "test",
        [SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        additional_properties={"test": "test"},
    )
    # Test that Security S0 Inclusion strategy can't be combined with a provisioning
    # entry
    with pytest.raises(ValueError):
        await controller.async_replace_failed_node(
            multisensor_6,
            InclusionStrategy.SECURITY_S0,
            provisioning=provisioning_entry,
        )
    # Test that Security S2 inclusion strategy can't use force_security
    with pytest.raises(ValueError):
        await controller.async_replace_failed_node(
            multisensor_6, InclusionStrategy.SECURITY_S2, force_security=True
        )


async def test_heal_node(controller, multisensor_6, uuid4, mock_command):
    """Test heal node."""
    ack_commands = mock_command(
        {"command": "controller.heal_node"},
        {"success": True},
    )

    assert await controller.async_heal_node(multisensor_6)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.heal_node",
        "messageId": uuid4,
        "nodeId": multisensor_6.node_id,
    }


async def test_begin_healing_network(controller, uuid4, mock_command):
    """Test begin healing network."""
    ack_commands = mock_command(
        {"command": "controller.begin_healing_network"},
        {"success": True},
    )

    assert await controller.async_begin_healing_network()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_healing_network",
        "messageId": uuid4,
    }


async def test_stop_healing_network(controller, uuid4, mock_command):
    """Test stop healing network."""
    ack_commands = mock_command(
        {"command": "controller.stop_healing_network"},
        {"success": True},
    )

    event = Event(
        "heal network progress",
        {
            "source": "controller",
            "event": "heal network progress",
            "progress": {52: "pending"},
        },
    )
    controller.receive_event(event)

    assert controller.heal_network_progress == {52: "pending"}
    assert await controller.async_stop_healing_network()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_healing_network",
        "messageId": uuid4,
    }
    # Verify that controller.heal_network_progress is cleared
    assert controller.heal_network_progress is None


async def test_is_failed_node(controller, multisensor_6, uuid4, mock_command):
    """Test is failed node."""
    ack_commands = mock_command(
        {"command": "controller.is_failed_node"},
        {"failed": False},
    )

    assert await controller.async_is_failed_node(multisensor_6) is False

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.is_failed_node",
        "messageId": uuid4,
        "nodeId": multisensor_6.node_id,
    }


async def test_get_association_groups(controller, uuid4, mock_command):
    """Test get association groups."""

    issued_commands = {2: [37, 43, 43], 5: [50, 114]}

    ack_commands = mock_command(
        {"command": "controller.get_association_groups"},
        {
            "groups": {
                1: {
                    "maxNodes": 10,
                    "isLifeline": True,
                    "multiChannel": True,
                    "label": "Association Group 1",
                },
                2: {
                    "maxNodes": 30,
                    "isLifeline": False,
                    "multiChannel": False,
                    "label": "Association Group 2",
                    "profile": 2,
                    "issuedCommands": issued_commands,
                },
            }
        },
    )

    association_address = association_pkg.AssociationAddress(node_id=52)
    result = await controller.async_get_association_groups(association_address)

    assert result[1].max_nodes == 10
    assert result[1].is_lifeline is True
    assert result[1].multi_channel is True
    assert result[1].label == "Association Group 1"
    assert result[1].profile is None
    assert result[1].issued_commands == {}

    assert result[2].max_nodes == 30
    assert result[2].is_lifeline is False
    assert result[2].multi_channel is False
    assert result[2].label == "Association Group 2"
    assert result[2].profile == 2
    for attr, value in issued_commands.items():
        assert result[2].issued_commands[attr] == value

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_association_groups",
        "messageId": uuid4,
        "nodeId": association_address.node_id,
    }


async def test_get_associations(controller, uuid4, mock_command):
    """Test get associations."""

    ack_commands = mock_command(
        {"command": "controller.get_associations"},
        {
            "associations": {
                "1": [
                    {"nodeId": 10},
                ],
                "2": [
                    {"nodeId": 11},
                    {"nodeId": 20},
                ],
                "3": [
                    {"nodeId": 30, "endpoint": 0},
                    {"nodeId": 40, "endpoint": 1},
                ],
            }
        },
    )

    association_address = association_pkg.AssociationAddress(node_id=52)
    result = await controller.async_get_associations(association_address)

    assert result[1][0].node_id == 10
    assert result[1][0].endpoint is None

    assert result[2][0].node_id == 11
    assert result[2][0].endpoint is None

    assert result[2][1].node_id == 20
    assert result[2][1].endpoint is None

    assert result[3][0].node_id == 30
    assert result[3][0].endpoint == 0

    assert result[3][1].node_id == 40
    assert result[3][1].endpoint == 1

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_associations",
        "messageId": uuid4,
        "nodeId": association_address.node_id,
    }


async def test_is_association_allowed(controller, uuid4, mock_command):
    """Test is association allowed."""

    ack_commands = mock_command(
        {"command": "controller.is_association_allowed"},
        {"allowed": True},
    )

    association_address = association_pkg.AssociationAddress(node_id=52)
    group = 0
    association = association_pkg.AssociationAddress(node_id=5, endpoint=0)

    assert await controller.async_is_association_allowed(
        association_address, group, association
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.is_association_allowed",
        "messageId": uuid4,
        "nodeId": association_address.node_id,
        "group": group,
        "association": {"nodeId": 5, "endpoint": 0},
    }


async def test_add_associations(controller, uuid4, mock_command):
    """Test add associations."""

    ack_commands = mock_command(
        {"command": "controller.add_associations"},
        {},
    )

    association_address = association_pkg.AssociationAddress(node_id=52)
    group = 0
    associations = [
        association_pkg.AssociationAddress(node_id=5, endpoint=0),
        association_pkg.AssociationAddress(node_id=10),
    ]

    await controller.async_add_associations(association_address, group, associations)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.add_associations",
        "messageId": uuid4,
        "nodeId": association_address.node_id,
        "group": group,
        "associations": [
            {"nodeId": associations[0].node_id, "endpoint": associations[0].endpoint},
            {"nodeId": associations[1].node_id},
        ],
    }

    association_address = association_pkg.AssociationAddress(node_id=52, endpoint=111)
    group = 1
    associations = [
        association_pkg.AssociationAddress(node_id=11),
        association_pkg.AssociationAddress(node_id=6, endpoint=1),
    ]

    await controller.async_add_associations(
        association_address, group, associations, True
    )

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "controller.add_associations",
        "messageId": uuid4,
        "nodeId": association_address.node_id,
        "endpoint": association_address.endpoint,
        "group": group,
        "associations": [
            {"nodeId": associations[0].node_id},
            {"nodeId": associations[1].node_id, "endpoint": associations[1].endpoint},
        ],
    }


async def test_remove_associations(controller, uuid4, mock_command):
    """Test remove associations."""

    ack_commands = mock_command(
        {"command": "controller.remove_associations"},
        {},
    )

    association_address = association_pkg.AssociationAddress(node_id=52)
    group = 0
    associations = [
        association_pkg.AssociationAddress(node_id=5, endpoint=0),
        association_pkg.AssociationAddress(node_id=10),
    ]

    await controller.async_remove_associations(association_address, group, associations)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.remove_associations",
        "messageId": uuid4,
        "nodeId": association_address.node_id,
        "group": group,
        "associations": [
            {"nodeId": associations[0].node_id, "endpoint": associations[0].endpoint},
            {"nodeId": associations[1].node_id},
        ],
    }

    association_address = association_pkg.AssociationAddress(node_id=53, endpoint=112)
    group = 1
    associations = [
        association_pkg.AssociationAddress(node_id=11),
        association_pkg.AssociationAddress(node_id=6, endpoint=1),
    ]

    await controller.async_remove_associations(
        association_address, group, associations, True
    )

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "controller.remove_associations",
        "messageId": uuid4,
        "nodeId": association_address.node_id,
        "endpoint": association_address.endpoint,
        "group": group,
        "associations": [
            {"nodeId": associations[0].node_id},
            {"nodeId": associations[1].node_id, "endpoint": associations[1].endpoint},
        ],
    }


async def test_remove_node_from_all_associations(
    controller, multisensor_6, uuid4, mock_command
):
    """Test remove associations."""

    ack_commands = mock_command(
        {"command": "controller.remove_node_from_all_associations"},
        {},
    )

    await controller.async_remove_node_from_all_associations(multisensor_6)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.remove_node_from_all_associations",
        "messageId": uuid4,
        "nodeId": multisensor_6.node_id,
    }

    await controller.async_remove_node_from_all_associations(multisensor_6, True)

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "controller.remove_node_from_all_associations",
        "messageId": uuid4,
        "nodeId": multisensor_6.node_id,
    }


async def test_get_node_neighbors(controller, multisensor_6, uuid4, mock_command):
    """Test get node neighbors."""

    ack_commands = mock_command(
        {"command": "controller.get_node_neighbors"}, {"neighbors": [1, 2]}
    )

    assert await controller.async_get_node_neighbors(multisensor_6) == [1, 2]

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_node_neighbors",
        "messageId": uuid4,
        "nodeId": multisensor_6.node_id,
    }


async def test_heal_network_active(client, controller):
    """Test that is_heal_network_active changes on events."""
    assert controller.is_heal_network_active is False
    assert controller.heal_network_progress is None
    event = Event(
        "heal network progress",
        {
            "source": "controller",
            "event": "heal network progress",
            "progress": {52: "pending"},
        },
    )
    controller.receive_event(event)
    assert controller.heal_network_progress == {52: "pending"}
    assert controller.is_heal_network_active
    event = Event(
        "heal network done",
        {
            "source": "controller",
            "event": "heal network done",
            "result": {52: "failed"},
        },
    )
    controller.receive_event(event)
    assert controller.heal_network_progress is None
    assert controller.is_heal_network_active is False


async def test_statistics_updated(controller):
    """Test that statistics get updated on events."""
    assert controller.statistics.nak == 0
    statistics_data = {
        "messagesTX": 1,
        "messagesRX": 1,
        "messagesDroppedRX": 1,
        "NAK": 1,
        "CAN": 1,
        "timeoutACK": 1,
        "timeoutResponse": 1,
        "timeoutCallback": 1,
        "messagesDroppedTX": 1,
    }
    assert controller.data.get("statistics") != statistics_data
    event = Event(
        "statistics updated",
        {
            "source": "controller",
            "event": "statistics updated",
            "statistics": statistics_data,
        },
    )
    controller.receive_event(event)
    # Event should be modified with the ControllerStatistics object
    assert "statistics_updated" in event.data
    event_stats = event.data["statistics_updated"]
    assert isinstance(event_stats, ControllerStatistics)
    assert controller.statistics.nak == 1
    assert controller.statistics == event_stats
    assert controller.data["statistics"] == statistics_data


async def test_grant_security_classes(controller, uuid4, mock_command) -> None:
    """Test controller.grant_security_classes command and event."""
    ack_commands = mock_command({"command": "controller.grant_security_classes"}, {})
    inclusion_grant = controller_pkg.InclusionGrant(
        [SecurityClass.S2_AUTHENTICATED], True
    )
    inclusion_grant_dict = {
        "securityClasses": [SecurityClass.S2_AUTHENTICATED.value],
        "clientSideAuth": True,
    }
    await controller.async_grant_security_classes(inclusion_grant)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.grant_security_classes",
        "messageId": uuid4,
        "inclusionGrant": inclusion_grant_dict,
    }

    # Test grant security classes event
    event = Event(
        "grant security classes",
        {
            "source": "controller",
            "event": "grant security classes",
            "requested": inclusion_grant_dict,
        },
    )
    controller.receive_event(event)
    assert event.data["requested_grant"] == inclusion_grant


async def test_validate_dsk_and_enter_pin(controller, uuid4, mock_command) -> None:
    """Test controller.validate_dsk_and_enter_pin command."""
    ack_commands = mock_command(
        {"command": "controller.validate_dsk_and_enter_pin"}, {}
    )
    await controller.async_validate_dsk_and_enter_pin("test")

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.validate_dsk_and_enter_pin",
        "messageId": uuid4,
        "pin": "test",
    }


async def test_supports_feature(controller, uuid4, mock_command):
    """Test supports feature."""
    ack_commands = mock_command(
        {"command": "controller.supports_feature"},
        {"supported": True},
    )
    assert await controller.async_supports_feature(ZwaveFeature.SMART_START)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.supports_feature",
        "feature": ZwaveFeature.SMART_START.value,
        "messageId": uuid4,
    }


async def test_get_state(controller, controller_state, uuid4, mock_command):
    """Test get state."""
    new_state = deepcopy(controller_state)
    new_state["inclusionState"] = 1
    ack_commands = mock_command(
        {"command": "controller.get_state"},
        {"state": new_state},
    )
    assert controller.inclusion_state == InclusionState.IDLE
    assert await controller.async_get_state() == new_state
    # Verify state hasn't changed
    assert controller.inclusion_state == InclusionState.IDLE

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_state",
        "messageId": uuid4,
    }


async def test_backup_nvm_raw(controller, uuid4, mock_command):
    """Test backup NVM raw."""
    ack_commands = mock_command(
        {"command": "controller.backup_nvm_raw"},
        {"nvmData": "AAAAAAAAAAAAAA=="},
    )
    assert await controller.async_backup_nvm_raw() == bytes(10)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.backup_nvm_raw",
        "messageId": uuid4,
    }


async def test_restore_nvm(controller, uuid4, mock_command):
    """Test restore NVM."""
    ack_commands = mock_command(
        {"command": "controller.restore_nvm"},
        {},
    )
    await controller.async_restore_nvm(bytes(10))

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.restore_nvm",
        "nvmData": "AAAAAAAAAAAAAA==",
        "messageId": uuid4,
    }


async def test_set_power_level(controller, uuid4, mock_command):
    """Test set powerlevel."""
    ack_commands = mock_command(
        {"command": "controller.set_powerlevel"},
        {"success": True},
    )
    assert await controller.async_set_power_level(1, 2)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.set_powerlevel",
        "powerlevel": 1,
        "measured0dBm": 2,
        "messageId": uuid4,
    }


async def test_get_power_level(controller, uuid4, mock_command):
    """Test get powerlevel."""
    ack_commands = mock_command(
        {"command": "controller.get_powerlevel"},
        {"powerlevel": 1, "measured0dBm": 2},
    )
    assert await controller.async_get_power_level() == {
        "power_level": 1,
        "measured_0_dbm": 2,
    }

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_powerlevel",
        "messageId": uuid4,
    }


async def test_set_rf_region(controller, uuid4, mock_command):
    """Test set RF region."""
    ack_commands = mock_command(
        {"command": "controller.set_rf_region"},
        {"success": True},
    )
    assert await controller.async_set_rf_region(RFRegion.USA)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.set_rf_region",
        "region": RFRegion.USA.value,
        "messageId": uuid4,
    }


async def test_get_rf_region(controller, uuid4, mock_command):
    """Test get RF region."""
    ack_commands = mock_command(
        {"command": "controller.get_rf_region"},
        {"region": 1},
    )
    assert await controller.async_get_rf_region() == RFRegion.USA

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_rf_region",
        "messageId": uuid4,
    }


async def test_get_known_lifeline_routes(
    multisensor_6, ring_keypad, wallmote_central_scene, uuid4, mock_command
):
    """Test get known lifeline routes."""
    ack_commands = mock_command(
        {"command": "controller.get_known_lifeline_routes"},
        {
            "routes": {
                multisensor_6.node_id: {
                    "lwr": {
                        "protocolDataRate": 1,
                        "repeaters": [multisensor_6.node_id],
                        "repeaterRSSI": [1],
                        "routeFailedBetween": [
                            ring_keypad.node_id,
                            wallmote_central_scene.node_id,
                        ],
                    },
                    "nlwr": {
                        "protocolDataRate": 2,
                        "repeaters": [],
                        "rssi": 1,
                        "repeaterRSSI": [127],
                    },
                }
            }
        },
    )
    routes = (
        await multisensor_6.client.driver.controller.async_get_known_lifeline_routes()
    )
    assert len(routes) == 1
    assert multisensor_6 in routes
    lifeline_routes = routes[multisensor_6]
    assert lifeline_routes.lwr
    assert lifeline_routes.lwr.protocol_data_rate == ProtocolDataRate.ZWAVE_9K6
    assert lifeline_routes.lwr.repeaters == [multisensor_6]
    assert not lifeline_routes.lwr.rssi
    assert lifeline_routes.lwr.repeater_rssi == [1]
    assert lifeline_routes.lwr.route_failed_between == (
        ring_keypad,
        wallmote_central_scene,
    )
    assert lifeline_routes.nlwr
    assert lifeline_routes.nlwr.protocol_data_rate == ProtocolDataRate.ZWAVE_40K
    assert lifeline_routes.nlwr.repeaters == []
    assert lifeline_routes.nlwr.rssi == 1
    with pytest.raises(RepeaterRssiErrorReceived):
        assert lifeline_routes.nlwr.repeater_rssi
    assert not lifeline_routes.nlwr.route_failed_between

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_known_lifeline_routes",
        "messageId": uuid4,
    }


async def test_is_any_ota_firmware_update_in_progress(
    multisensor_6, uuid4, mock_command
):
    """Test get any firmware update progress."""
    ack_commands = mock_command(
        {"command": "controller.is_any_ota_firmware_update_in_progress"},
        {"progress": False},
    )
    controller = multisensor_6.client.driver.controller
    assert not await controller.async_is_any_ota_firmware_update_in_progress()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.is_any_ota_firmware_update_in_progress",
        "messageId": uuid4,
    }


async def test_get_available_firmware_updates(multisensor_6, uuid4, mock_command):
    """Test get available firmware updates."""
    ack_commands = mock_command(
        {"command": "controller.get_available_firmware_updates"},
        {
            "updates": [
                {
                    "version": "1.0.0",
                    "changelog": "changelog",
                    "files": [
                        {"target": 0, "url": "http://example.com", "integrity": "test"}
                    ],
                }
            ]
        },
    )
    updates = await multisensor_6.client.driver.controller.async_get_available_firmware_updates(
        multisensor_6, "test"
    )

    assert len(updates) == 1
    update = updates[0]
    assert update.version == "1.0.0"
    assert update.changelog == "changelog"
    assert len(update.files) == 1
    file = update.files[0]
    assert file.target == 0
    assert file.url == "http://example.com"
    assert file.integrity == "test"

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_available_firmware_updates",
        "nodeId": multisensor_6.node_id,
        "apiKey": "test",
        "includePrereleases": False,
        "messageId": uuid4,
    }


async def test_begin_ota_firmware_update(multisensor_6, uuid4, mock_command):
    """Test get available firmware updates."""
    ack_commands = mock_command(
        {"command": "controller.firmware_update_ota"},
        {"success": True},
    )
    assert await multisensor_6.client.driver.controller.async_firmware_update_ota(
        multisensor_6,
        [
            NodeFirmwareUpdateFileInfo(
                target=0, url="http://example.com", integrity="test"
            )
        ],
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.firmware_update_ota",
        "nodeId": multisensor_6.node_id,
        "updates": [{"target": 0, "url": "http://example.com", "integrity": "test"}],
        "messageId": uuid4,
    }


async def test_get_known_lifeline_routes_rssi_error(
    multisensor_6, ring_keypad, wallmote_central_scene, uuid4, mock_command
):
    """Test get known lifeline routes has an RSSI error."""
    ack_commands = mock_command(
        {"command": "controller.get_known_lifeline_routes"},
        {
            "routes": {
                multisensor_6.node_id: {
                    "lwr": {
                        "protocolDataRate": 1,
                        "repeaters": [multisensor_6.node_id],
                        "repeaterRSSI": [1],
                        "routeFailedBetween": [
                            ring_keypad.node_id,
                            wallmote_central_scene.node_id,
                        ],
                    },
                    "nlwr": {
                        "protocolDataRate": 2,
                        "repeaters": [],
                        "rssi": 127,
                        "repeaterRSSI": [127],
                    },
                }
            }
        },
    )
    routes = (
        await multisensor_6.client.driver.controller.async_get_known_lifeline_routes()
    )
    assert len(routes) == 1
    assert multisensor_6 in routes
    lifeline_routes = routes[multisensor_6]
    with pytest.raises(RssiErrorReceived):
        assert lifeline_routes.nlwr.rssi

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_known_lifeline_routes",
        "messageId": uuid4,
    }


async def test_is_firmware_update_in_progress(
    controller, uuid4, mock_command
):
    """Test is_firmware_update_in_progress command."""
    ack_commands = mock_command(
        {"command": "controller.is_firmware_update_in_progress"},
        {"progress": True},
    )
    assert await controller.async_is_firmware_update_in_progress()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.provision_smart_start_node",
        "messageId": uuid4,
    }


async def test_nvm_events(controller):
    """Test NVM progress events."""
    event = Event(
        "nvm backup progress",
        {
            "source": "controller",
            "event": "nvm backup progress",
            "bytesRead": 1,
            "total": 2,
        },
    )
    controller.receive_event(event)
    assert event.data["nvm_backup_progress"] == controller_pkg.NVMProgress(1, 2)

    event = Event(
        "nvm convert progress",
        {
            "source": "controller",
            "event": "nvm convert progress",
            "bytesRead": 3,
            "total": 4,
        },
    )
    controller.receive_event(event)
    assert event.data["nvm_convert_progress"] == controller_pkg.NVMProgress(3, 4)

    event = Event(
        "nvm restore progress",
        {
            "source": "controller",
            "event": "nvm restore progress",
            "bytesWritten": 5,
            "total": 6,
        },
    )
    controller.receive_event(event)
    assert event.data["nvm_restore_progress"] == controller_pkg.NVMProgress(5, 6)


async def test_node_found(controller):
    """Test node found event."""
    found_node = {
        "id": 1,
        "deviceClass": {
            "basic": {"key": 2, "label": "1"},
            "generic": {"key": 3, "label": "2"},
            "specific": {"key": 4, "label": "3"},
            "mandatorySupportedCCs": [112],
            "mandatoryControlledCCs": [112],
        },
        "supportedCCs": [112],
        "controlledCCs": [112],
    }
    event = Event(
        "node found",
        {
            "source": "controller",
            "event": "node found",
            "node": found_node,
        },
    )
    controller.receive_event(event)
    assert event.data["node"] == found_node


async def test_node_added(controller, multisensor_6_state):
    """Test node added event."""
    event = Event(
        "node added",
        {
            "source": "controller",
            "event": "node added",
            "node": multisensor_6_state,
            "result": "",
        },
    )
    controller.receive_event(event)
    assert event.data["node"].node_id == 52


async def test_node_removed(client, multisensor_6, multisensor_6_state):
    """Test node removed event."""
    event = Event(
        "node removed",
        {
            "source": "controller",
            "event": "node removed",
            "node": multisensor_6_state,
            "replaced": False,
        },
    )
    client.driver.controller.receive_event(event)
    assert event.data["node"].node_id == 52
    assert event.data["node"].client is None
    assert 52 not in client.driver.controller.nodes


async def test_inclusion_aborted(controller):
    """Test inclusion aborted event."""
    event_data = {
        "source": "controller",
        "event": "inclusion aborted",
    }
    event = Event("inclusion aborted", event_data.copy())
    with patch(
        "zwave_js_server.model.controller.Controller.handle_inclusion_aborted"
    ) as mock:
        controller.receive_event(event)
        assert mock.called

    # Ensure that the handler doesn't modify the event
    assert {k: v for k, v in event.data.items() if k != "controller"} == event_data


async def test_firmware_events(controller):
    """Test firmware events."""
    assert controller.firmware_update_progress is None
    event = Event(
        type="firmware update progress",
        data={
            "source": "controller",
            "event": "firmware update progress",
            "progress": {
                "sentFragments": 1,
                "totalFragments": 10,
                "progress": 10.0,
            },
        },
    )

    controller.receive_event(event)
    progress = event.data["firmware_update_progress"]
    assert progress.sent_fragments == 1
    assert progress.total_fragments == 10
    assert progress.progress == 10.0
    assert controller.firmware_update_progress
    assert controller.firmware_update_progress.sent_fragments == 1
    assert controller.firmware_update_progress.total_fragments == 10
    assert controller.firmware_update_progress.progress == 10.0

    event = Event(
        type="firmware update finished",
        data={
            "source": "controller",
            "event": "firmware update finished",
            "result": {"status": 255, "success": True},
        },
    )

    controller.receive_event(event)
    result = event.data["firmware_update_finished"]
    assert result.status == ControllerFirmwareUpdateStatus.OK
    assert result.success
    assert controller.firmware_update_progress is None


async def test_unknown_event(controller):
    """Test that an unknown event type causes an exception."""
    with pytest.raises(KeyError):
        assert controller.receive_event(
            Event("unknown_event", {"source": "controller"})
        )


async def test_additional_events(controller):
    """Test that remaining events pass pydantic validation."""
    event = Event(
        "exclusion failed", {"source": "controller", "event": "exclusion failed"}
    )
    controller.receive_event(event)
    event = Event(
        "exclusion started", {"source": "controller", "event": "exclusion started"}
    )
    controller.receive_event(event)
    event = Event(
        "exclusion stopped", {"source": "controller", "event": "exclusion stopped"}
    )
    controller.receive_event(event)
    event = Event(
        "inclusion failed", {"source": "controller", "event": "inclusion failed"}
    )
    controller.receive_event(event)
    event = Event(
        "inclusion started",
        {"source": "controller", "event": "inclusion started", "secure": True},
    )
    controller.receive_event(event)
    event = Event(
        "inclusion stopped", {"source": "controller", "event": "inclusion stopped"}
    )
    controller.receive_event(event)
    event = Event(
        "validate dsk and enter pin",
        {"source": "controller", "event": "validate dsk and enter pin", "dsk": "1234"},
    )
    controller.receive_event(event)
