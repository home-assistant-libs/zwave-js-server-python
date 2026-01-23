"""Test the controller model."""

from copy import deepcopy
import json
import logging
from unittest.mock import patch

import pytest

from zwave_js_server.const import (
    AssociationCheckResult,
    ControllerStatus,
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
from zwave_js_server.model import (
    association as association_pkg,
    controller as controller_pkg,
)
from zwave_js_server.model.controller import Controller
from zwave_js_server.model.controller.rebuild_routes import (
    RebuildRoutesOptions,
    RebuildRoutesStatus,
)
from zwave_js_server.model.controller.statistics import ControllerStatistics
from zwave_js_server.model.node import Node
from zwave_js_server.model.node.firmware import NodeFirmwareUpdateInfo

from .. import load_fixture
from .common import FIRMWARE_UPDATE_INFO


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
    assert ctrl.is_rebuilding_routes is False
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
    assert ctrl.rebuild_routes_progress is None


def test_controller_mods(client):
    """Test modifications to controller method."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["result"]["state"]
    state["controller"].pop("ownNodeId")
    state["controller"]["rfRegion"] = 0
    state["controller"]["status"] = 0
    state["controller"]["rebuildRoutesProgress"] = {1: "pending"}
    state["controller"]["supportsLongRange"] = True

    ctrl = controller_pkg.Controller(client, state)
    assert ctrl.own_node_id is None
    assert ctrl.own_node is None
    assert ctrl.rf_region == RFRegion.EUROPE
    assert ctrl.status == ControllerStatus.READY
    assert ctrl.rebuild_routes_progress == {ctrl.nodes[1]: RebuildRoutesStatus.PENDING}
    assert ctrl.supports_long_range is True


def test_controller_status():
    """Test controller status functionality."""
    state = json.loads(load_fixture("basic_dump.txt").split("\n")[0])["result"]["state"]
    state["controller"]["status"] = 0

    ctrl = controller_pkg.Controller(None, state)
    assert ctrl.status == ControllerStatus.READY
    event = Event(
        "status changed",
        {"source": "controller", "event": "status changed", "status": 1},
    )
    ctrl.receive_event(event)
    assert ctrl.status == ControllerStatus.UNRESPONSIVE


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


async def test_begin_inclusion_s2_dsk(controller, uuid4, mock_command):
    """Test begin inclusion S2 Mode with DSK string."""
    ack_commands = mock_command(
        {"command": "controller.begin_inclusion"},
        {"success": True},
    )
    assert await controller.async_begin_inclusion(
        InclusionStrategy.SECURITY_S2, dsk="test"
    )

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_inclusion",
        "options": {
            "strategy": InclusionStrategy.SECURITY_S2,
            "dsk": "test",
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

    # Test that Security S0 Inclusion Strategy doesn't support providing a DSK string
    with pytest.raises(ValueError):
        await controller.async_begin_inclusion(
            InclusionStrategy.SECURITY_S0, dsk="test"
        )

    # Test that Security S2 Inclusion Strategy doesn't support providing
    # `force_security`
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

    provisioning_entry = controller_pkg.ProvisioningEntry(
        "test",
        [SecurityClass.S2_UNAUTHENTICATED],
        requested_security_classes=[SecurityClass.S2_UNAUTHENTICATED],
        additional_properties={"test": "test"},
    )
    # Test that provisioning entry and dsk string can't be provided together
    with pytest.raises(ValueError):
        await controller.async_begin_inclusion(
            InclusionStrategy.SECURITY_S2, provisioning=provisioning_entry, dsk="test"
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

    ack_commands.clear()

    # Test that when supported protocols aren't included, it should be None
    # instead of an empty list.
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
        supported_protocols=None,
    )
    await controller.async_provision_smart_start_node(provisioning_entry)

    qr_entry = {
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
    }

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.provision_smart_start_node",
        "entry": qr_entry,
        "messageId": uuid4,
    }

    assert (
        qr_entry
        == controller_pkg.QRProvisioningInformation.from_dict(qr_entry).to_dict()
    )

    assert controller_pkg.QRProvisioningInformation(
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
        additional_properties={"test": "foo"},
    ) == controller_pkg.QRProvisioningInformation.from_dict(
        {
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
            "test": "foo",
        }
    )

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


async def test_cancel_secure_bootstrap_s2(controller, uuid4, mock_command):
    """Test cancel secure bootstrap S2."""
    ack_commands = mock_command(
        {"command": "controller.cancel_secure_bootstrap_s2"},
        {},
    )
    assert await controller.async_cancel_secure_bootstrap_s2() is None

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.cancel_secure_bootstrap_s2",
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
        "options": {"strategy": ExclusionStrategy.EXCLUDE_ONLY},
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


async def test_rebuild_node_routes(controller, multisensor_6, uuid4, mock_command):
    """Test rebuild node routes."""
    ack_commands = mock_command(
        {"command": "controller.rebuild_node_routes"},
        {"success": True},
    )

    assert await controller.async_rebuild_node_routes(multisensor_6)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.rebuild_node_routes",
        "messageId": uuid4,
        "nodeId": multisensor_6.node_id,
    }


async def test_begin_rebuilding_routes(controller, uuid4, mock_command):
    """Test begin rebuilding routes."""
    ack_commands = mock_command(
        {"command": "controller.begin_rebuilding_routes"},
        {"success": True},
    )

    assert await controller.async_begin_rebuilding_routes()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_rebuilding_routes",
        "messageId": uuid4,
    }

    options_include_sleeping = RebuildRoutesOptions(True)
    assert await controller.async_begin_rebuilding_routes(options_include_sleeping)

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "controller.begin_rebuilding_routes",
        "options": {"includeSleeping": True},
        "messageId": uuid4,
    }

    assert await controller.async_begin_rebuilding_routes(RebuildRoutesOptions())

    assert len(ack_commands) == 3
    assert ack_commands[2] == {
        "command": "controller.begin_rebuilding_routes",
        "options": {},
        "messageId": uuid4,
    }

    assert (
        RebuildRoutesOptions.from_dict({"includeSleeping": True})
        == options_include_sleeping
    )


async def test_stop_rebuilding_routes(client, multisensor_6, uuid4, mock_command):
    """Test stop rebuilding routes."""
    controller = client.driver.controller
    ack_commands = mock_command(
        {"command": "controller.stop_rebuilding_routes"},
        {"success": True},
    )

    event = Event(
        "rebuild routes progress",
        {
            "source": "controller",
            "event": "rebuild routes progress",
            "progress": {"52": "pending"},
        },
    )
    controller.receive_event(event)

    assert controller.rebuild_routes_progress == {
        multisensor_6: RebuildRoutesStatus.PENDING
    }
    assert await controller.async_stop_rebuilding_routes()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_rebuilding_routes",
        "messageId": uuid4,
    }
    # Verify that controller.rebuild_routes_progress is cleared
    assert controller.rebuild_routes_progress is None


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
                "1": {
                    "maxNodes": 10,
                    "isLifeline": True,
                    "multiChannel": True,
                    "label": "Association Group 1",
                },
                "2": {
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

    assoc_addr = association_pkg.AssociationAddress(controller, node_id=52)
    result = await controller.async_get_association_groups(assoc_addr)

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
        "nodeId": assoc_addr.node_id,
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

    assoc_addr = association_pkg.AssociationAddress(controller, node_id=52)
    result = await controller.async_get_associations(assoc_addr)

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
        "nodeId": assoc_addr.node_id,
    }


async def test_assoc_addr_model(client, multisensor_6, uuid4, mock_command):
    """Test association address model."""

    cls_ = association_pkg.AssociationAddress
    controller = client.driver.controller
    assert cls_(controller, node_id=52).node == multisensor_6
    assert cls_(controller, node_id=255).node is None


async def test_check_association(controller, uuid4, mock_command):
    """Test is association allowed."""

    ack_commands = mock_command(
        {"command": "controller.check_association"},
        {"result": 1},
    )

    assoc_addr = association_pkg.AssociationAddress(controller, node_id=52)
    group = 0
    assoc = association_pkg.AssociationAddress(controller, node_id=5, endpoint=0)

    result = await controller.async_check_association(assoc_addr, group, assoc)
    assert result is AssociationCheckResult.OK

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.check_association",
        "messageId": uuid4,
        "nodeId": assoc_addr.node_id,
        "group": group,
        "association": {"nodeId": 5, "endpoint": 0},
    }


async def test_add_associations(controller, uuid4, mock_command):
    """Test add associations."""

    ack_commands = mock_command(
        {"command": "controller.add_associations"},
        {},
    )

    assoc_addr = association_pkg.AssociationAddress(controller, node_id=52)
    group = 0
    associations = [
        association_pkg.AssociationAddress(controller, node_id=5, endpoint=0),
        association_pkg.AssociationAddress(controller, node_id=10),
    ]

    await controller.async_add_associations(assoc_addr, group, associations)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.add_associations",
        "messageId": uuid4,
        "nodeId": assoc_addr.node_id,
        "group": group,
        "associations": [
            {"nodeId": associations[0].node_id, "endpoint": associations[0].endpoint},
            {"nodeId": associations[1].node_id},
        ],
    }

    assoc_addr = association_pkg.AssociationAddress(
        controller, node_id=52, endpoint=111
    )
    group = 1
    associations = [
        association_pkg.AssociationAddress(controller, node_id=11),
        association_pkg.AssociationAddress(controller, node_id=6, endpoint=1),
    ]

    await controller.async_add_associations(assoc_addr, group, associations, True)

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "controller.add_associations",
        "messageId": uuid4,
        "nodeId": assoc_addr.node_id,
        "endpoint": assoc_addr.endpoint,
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

    assoc_addr = association_pkg.AssociationAddress(controller, node_id=52)
    group = 0
    associations = [
        association_pkg.AssociationAddress(controller, node_id=5, endpoint=0),
        association_pkg.AssociationAddress(controller, node_id=10),
    ]

    await controller.async_remove_associations(assoc_addr, group, associations)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.remove_associations",
        "messageId": uuid4,
        "nodeId": assoc_addr.node_id,
        "group": group,
        "associations": [
            {"nodeId": associations[0].node_id, "endpoint": associations[0].endpoint},
            {"nodeId": associations[1].node_id},
        ],
    }

    assoc_addr = association_pkg.AssociationAddress(
        controller, node_id=53, endpoint=112
    )
    group = 1
    associations = [
        association_pkg.AssociationAddress(controller, node_id=11),
        association_pkg.AssociationAddress(controller, node_id=6, endpoint=1),
    ]

    await controller.async_remove_associations(assoc_addr, group, associations, True)

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "controller.remove_associations",
        "messageId": uuid4,
        "nodeId": assoc_addr.node_id,
        "endpoint": assoc_addr.endpoint,
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


async def test_rebuild_routes_active(client, multisensor_6):
    """Test that is_rebuilding_routes changes on events."""
    controller = client.driver.controller
    assert controller.is_rebuilding_routes is False
    assert controller.rebuild_routes_progress is None
    event = Event(
        "rebuild routes progress",
        {
            "source": "controller",
            "event": "rebuild routes progress",
            "progress": {"52": "pending"},
        },
    )
    controller.receive_event(event)
    assert controller.rebuild_routes_progress == {
        multisensor_6: RebuildRoutesStatus.PENDING
    }
    assert controller.last_rebuild_routes_result is None
    assert controller.is_rebuilding_routes
    event = Event(
        "rebuild routes done",
        {
            "source": "controller",
            "event": "rebuild routes done",
            "result": {"52": "failed"},
        },
    )
    controller.receive_event(event)
    assert controller.rebuild_routes_progress is None
    assert controller.last_rebuild_routes_result == {
        multisensor_6: RebuildRoutesStatus.FAILED
    }
    assert controller.is_rebuilding_routes is False


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
    assert controller.statistics.nak == event_stats.nak == 1
    assert event_stats.background_rssi is None
    assert controller.statistics == event_stats
    assert controller.data["statistics"] == statistics_data

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
        "backgroundRSSI": {
            "timestamp": 1234567890,
            "channel0": {
                "average": -91,
                "current": -92,
            },
            "channel1": {
                "average": -93,
                "current": -94,
            },
        },
    }
    event = Event(
        "statistics updated",
        {
            "source": "controller",
            "event": "statistics updated",
            "statistics": statistics_data,
        },
    )
    controller.receive_event(event)
    event_stats = event.data["statistics_updated"]
    assert isinstance(event_stats, ControllerStatistics)
    assert event_stats.background_rssi
    assert event_stats.background_rssi.timestamp == 1234567890
    assert event_stats.background_rssi.channel_0.average == -91
    assert event_stats.background_rssi.channel_0.current == -92
    assert event_stats.background_rssi.channel_1.average == -93
    assert event_stats.background_rssi.channel_1.current == -94
    assert event_stats.background_rssi.channel_2 is None
    assert event_stats.background_rssi.channel_3 is None

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
        "backgroundRSSI": {
            "timestamp": 1234567890,
            "channel0": {
                "average": -81,
                "current": -82,
            },
            "channel1": {
                "average": -83,
                "current": -84,
            },
            "channel2": {
                "average": -85,
                "current": -86,
            },
        },
    }
    event = Event(
        "statistics updated",
        {
            "source": "controller",
            "event": "statistics updated",
            "statistics": statistics_data,
        },
    )
    controller.receive_event(event)
    event_stats = event.data["statistics_updated"]
    assert isinstance(event_stats, ControllerStatistics)
    assert event_stats.background_rssi
    assert event_stats.background_rssi.timestamp == 1234567890
    assert event_stats.background_rssi.channel_0.average == -81
    assert event_stats.background_rssi.channel_0.current == -82
    assert event_stats.background_rssi.channel_1.average == -83
    assert event_stats.background_rssi.channel_1.current == -84
    assert event_stats.background_rssi.channel_2.average == -85
    assert event_stats.background_rssi.channel_2.current == -86
    assert event_stats.background_rssi.channel_3 is None

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
        "backgroundRSSI": {
            "timestamp": 1234567890,
            "channel0": {
                "average": -81,
                "current": -82,
            },
            "channel1": {
                "average": -83,
                "current": -84,
            },
            "channel2": {
                "average": -85,
                "current": -86,
            },
            "channel3": {
                "average": -87,
                "current": -88,
            },
        },
    }
    event = Event(
        "statistics updated",
        {
            "source": "controller",
            "event": "statistics updated",
            "statistics": statistics_data,
        },
    )
    controller.receive_event(event)
    event_stats = event.data["statistics_updated"]
    assert isinstance(event_stats, ControllerStatistics)
    assert event_stats.background_rssi
    assert event_stats.background_rssi.channel_3.average == -87
    assert event_stats.background_rssi.channel_3.current == -88


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
    await controller.async_restore_nvm(bytes(10), {})

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.restore_nvm",
        "nvmData": "AAAAAAAAAAAAAA==",
        "messageId": uuid4,
        "migrateOptions": {},
    }

    await controller.async_restore_nvm(bytes(10), {"preserveRoutes": False})

    assert len(ack_commands) == 2
    assert ack_commands[1] == {
        "command": "controller.restore_nvm",
        "nvmData": "AAAAAAAAAAAAAA==",
        "messageId": uuid4,
        "migrateOptions": {"preserveRoutes": False},
    }


async def test_backup_nvm_raw_base64(controller, uuid4, mock_command):
    """Test backup NVM raw with base64 return."""
    ack_commands = mock_command(
        {"command": "controller.backup_nvm_raw"},
        {"nvmData": "AAAAAAAAAAAAAA=="},
    )
    assert await controller.async_backup_nvm_raw_base64() == "AAAAAAAAAAAAAA=="

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.backup_nvm_raw",
        "messageId": uuid4,
    }


async def test_restore_nvm_base64(controller, uuid4, mock_command):
    """Test restore NVM with base64 input."""
    ack_commands = mock_command(
        {"command": "controller.restore_nvm"},
        {},
    )
    await controller.async_restore_nvm_base64("AAAAAAAAAAAAAA==")

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.restore_nvm",
        "nvmData": "AAAAAAAAAAAAAA==",
        "messageId": uuid4,
        "migrateOptions": {},
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


async def test_toggle_rf(controller, uuid4, mock_command):
    """Test toggle RF."""
    ack_commands = mock_command(
        {"command": "controller.toggle_rf"},
        {"success": True},
    )
    assert await controller.async_toggle_rf(True)

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.toggle_rf",
        "enable": True,
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
                f"{multisensor_6.node_id}": {
                    "lwr": {
                        "protocolDataRate": 1,
                        "repeaters": [f"{multisensor_6.node_id}"],
                        "repeaterRSSI": [1],
                        "routeFailedBetween": [
                            f"{ring_keypad.node_id}",
                            f"{wallmote_central_scene.node_id}",
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


async def test_get_known_lifeline_routes_bad_protocol_data_rates(
    multisensor_6, uuid4, mock_command
):
    """Test get known lifeline routes with bad protocol data rates."""
    ack_commands = mock_command(
        {"command": "controller.get_known_lifeline_routes"},
        {
            "routes": {
                f"{multisensor_6.node_id}": {
                    "lwr": {
                        "protocolDataRate": 0,
                        "repeaters": [],
                        "repeaterRSSI": [],
                        "routeFailedBetween": [],
                    },
                    "nlwr": {
                        "protocolDataRate": 0,
                        "repeaters": [],
                        "rssi": 1,
                        "repeaterRSSI": [],
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
    assert not lifeline_routes.lwr
    assert not lifeline_routes.nlwr

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
        {"updates": [FIRMWARE_UPDATE_INFO]},
    )
    controller = multisensor_6.client.driver.controller
    updates = await controller.async_get_available_firmware_updates(
        multisensor_6, "test"
    )
    assert len(updates) == 1
    update = updates[0]
    assert update.version == "1.0.0"
    assert update.changelog == "changelog"
    assert update.channel == "stable"
    assert len(update.files) == 1
    file = update.files[0]
    assert file.target == 0
    assert file.url == "http://example.com"
    assert file.integrity == "test"
    assert update.downgrade
    assert update.normalized_version == "1.0.0"
    assert update.device.manufacturer_id == 1
    assert update.device.product_type == 2
    assert update.device.product_id == 3
    assert update.device.firmware_version == "0.4.4"
    assert update.device.rf_region == RFRegion.USA

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_available_firmware_updates",
        "nodeId": multisensor_6.node_id,
        "apiKey": "test",
        "includePrereleases": True,
        "messageId": uuid4,
    }


async def test_begin_ota_firmware_update(multisensor_6, uuid4, mock_command):
    """Test get available firmware updates."""
    ack_commands = mock_command(
        {"command": "controller.firmware_update_ota"},
        {"result": {"status": 255, "success": True, "reInterview": False}},
    )
    result = await multisensor_6.client.driver.controller.async_firmware_update_ota(
        multisensor_6, NodeFirmwareUpdateInfo.from_dict(FIRMWARE_UPDATE_INFO)
    )
    assert result.status == 255
    assert result.success
    assert not result.reinterview

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.firmware_update_ota",
        "nodeId": multisensor_6.node_id,
        "updateInfo": FIRMWARE_UPDATE_INFO,
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
                f"{multisensor_6.node_id}": {
                    "lwr": {
                        "protocolDataRate": 1,
                        "repeaters": [f"{multisensor_6.node_id}"],
                        "repeaterRSSI": [1],
                        "routeFailedBetween": [
                            f"{ring_keypad.node_id}",
                            f"{wallmote_central_scene.node_id}",
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


async def test_is_firmware_update_in_progress(controller, uuid4, mock_command):
    """Test is_firmware_update_in_progress command."""
    ack_commands = mock_command(
        {"command": "controller.is_firmware_update_in_progress"},
        {"progress": True},
    )
    assert await controller.async_is_firmware_update_in_progress()

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.is_firmware_update_in_progress",
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
            "result": {},
        },
    )
    controller.receive_event(event)
    assert event.data["node"].node_id == 52


async def test_node_removed(client, multisensor_6, multisensor_6_state):
    """Test node removed event."""
    assert 52 in client.driver.controller.nodes
    assert client.driver.controller.nodes[52] == multisensor_6
    event = Event(
        "node removed",
        {
            "source": "controller",
            "event": "node removed",
            "node": multisensor_6_state,
            "reason": 0,
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


async def test_unknown_event(controller, caplog):
    """Test that an unknown event type logs a message but does not raise."""
    caplog.set_level(logging.INFO)
    event = Event("unknown_event", {"source": "controller", "event": "unknown_event"})
    controller.receive_event(event)
    assert len(caplog.records) == 1
    assert "Unhandled controller event: unknown_event" in caplog.records[0].message
    assert caplog.records[0].levelno == logging.INFO


async def test_additional_events(controller: Controller) -> None:
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
        {"source": "controller", "event": "inclusion started", "strategy": 0},
    )
    controller.receive_event(event)
    event = Event(
        "inclusion state changed",
        {"source": "controller", "event": "inclusion state changed", "state": 1},
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


async def test_identify(client, multisensor_6):
    """Test identify event."""
    event = Event(
        "identify",
        {"source": "controller", "event": "identify", "nodeId": multisensor_6.node_id},
    )
    client.driver.controller.receive_event(event)
    assert event.data["node"] == multisensor_6


async def test_inclusion_state_changed(controller):
    """Test that inclusion state is updated after receiving inclusion state changed event."""
    assert controller.inclusion_state == InclusionState.IDLE
    event = Event(
        "inclusion state changed",
        {
            "source": "controller",
            "event": "inclusion state changed",
            "state": InclusionState.INCLUDING.value,
        },
    )
    controller.receive_event(event)
    assert controller.inclusion_state == InclusionState.INCLUDING


# Schema 45+ tests


async def test_get_background_rssi(controller, uuid4, mock_command):
    """Test get_background_rssi command."""
    ack_commands = mock_command(
        {"command": "controller.get_background_rssi"},
        {"rssiChannel0": -90, "rssiChannel1": -85, "rssiChannel2": -80},
    )

    result = await controller.async_get_background_rssi()
    assert result == {
        "rssiChannel0": -90,
        "rssiChannel1": -85,
        "rssiChannel2": -80,
        "rssiChannel3": None,
    }

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_background_rssi",
        "messageId": uuid4,
    }


async def test_get_long_range_nodes(controller, uuid4, mock_command):
    """Test get_long_range_nodes command."""
    ack_commands = mock_command(
        {"command": "controller.get_long_range_nodes"},
        {"nodeIds": [52, 53, 54]},
    )

    result = await controller.async_get_long_range_nodes()
    assert result == [52, 53, 54]

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_long_range_nodes",
        "messageId": uuid4,
    }


async def test_get_dsk(controller, uuid4, mock_command):
    """Test get_dsk command."""
    import base64

    dsk_bytes = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
    dsk_base64 = base64.b64encode(dsk_bytes).decode("utf-8")

    ack_commands = mock_command(
        {"command": "controller.get_dsk"},
        {"dsk": dsk_base64},
    )

    result = await controller.async_get_dsk()
    assert result == dsk_bytes

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_dsk",
        "messageId": uuid4,
    }


async def test_get_all_association_groups(
    controller, multisensor_6, uuid4, mock_command
):
    """Test get_all_association_groups command."""
    ack_commands = mock_command(
        {"command": "controller.get_all_association_groups"},
        {
            "groups": {
                "0": {
                    "1": {
                        "maxNodes": 5,
                        "isLifeline": True,
                        "multiChannel": True,
                        "label": "Lifeline",
                    }
                }
            }
        },
    )

    result = await controller.async_get_all_association_groups(multisensor_6)
    assert 0 in result
    assert 1 in result[0]
    group = result[0][1]
    assert group.max_nodes == 5
    assert group.is_lifeline is True
    assert group.multi_channel is True
    assert group.label == "Lifeline"

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_all_association_groups",
        "nodeId": multisensor_6.node_id,
        "messageId": uuid4,
    }


async def test_get_all_associations(controller, multisensor_6, uuid4, mock_command):
    """Test get_all_associations command."""
    ack_commands = mock_command(
        {"command": "controller.get_all_associations"},
        {"associations": {"52": {"1": [{"nodeId": 1}, {"nodeId": 5, "endpoint": 0}]}}},
    )

    result = await controller.async_get_all_associations(multisensor_6)
    # The endpoint_key "52" is parsed as endpoint 0 (no colon)
    assert 0 in result
    assert 1 in result[0]
    associations = result[0][1]
    assert len(associations) == 2
    assert associations[0].node_id == 1
    assert associations[0].endpoint is None
    assert associations[1].node_id == 5
    assert associations[1].endpoint == 0

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_all_associations",
        "nodeId": multisensor_6.node_id,
        "messageId": uuid4,
    }


async def test_get_all_available_firmware_updates(
    controller, multisensor_6, uuid4, mock_command
):
    """Test get_all_available_firmware_updates command."""
    ack_commands = mock_command(
        {"command": "controller.get_all_available_firmware_updates"},
        {
            "updates": {
                "52": [FIRMWARE_UPDATE_INFO],
            }
        },
    )

    result = await controller.async_get_all_available_firmware_updates("test-api-key")
    assert 52 in result
    assert len(result[52]) == 1
    update = result[52][0]
    assert update.version == "1.0.0"

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_all_available_firmware_updates",
        "apiKey": "test-api-key",
        "includePrereleases": True,
        "messageId": uuid4,
    }


async def test_begin_joining_network(controller, uuid4, mock_command):
    """Test begin_joining_network command."""
    ack_commands = mock_command(
        {"command": "controller.begin_joining_network"},
        {"result": {"status": "started"}},
    )

    result = await controller.async_begin_joining_network()
    assert result == {"status": "started"}

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_joining_network",
        "messageId": uuid4,
    }


async def test_stop_joining_network(controller, uuid4, mock_command):
    """Test stop_joining_network command."""
    ack_commands = mock_command(
        {"command": "controller.stop_joining_network"},
        {"success": True},
    )

    result = await controller.async_stop_joining_network()
    assert result is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_joining_network",
        "messageId": uuid4,
    }


async def test_begin_leaving_network(controller, uuid4, mock_command):
    """Test begin_leaving_network command."""
    ack_commands = mock_command(
        {"command": "controller.begin_leaving_network"},
        {"result": {"status": "started"}},
    )

    result = await controller.async_begin_leaving_network()
    assert result == {"status": "started"}

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.begin_leaving_network",
        "messageId": uuid4,
    }


async def test_stop_leaving_network(controller, uuid4, mock_command):
    """Test stop_leaving_network command."""
    ack_commands = mock_command(
        {"command": "controller.stop_leaving_network"},
        {"success": True},
    )

    result = await controller.async_stop_leaving_network()
    assert result is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_leaving_network",
        "messageId": uuid4,
    }


async def test_start_watchdog(controller, uuid4, mock_command):
    """Test start_watchdog command."""
    ack_commands = mock_command(
        {"command": "controller.start_watchdog"},
        {"success": True},
    )

    result = await controller.async_start_watchdog()
    assert result is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.start_watchdog",
        "messageId": uuid4,
    }


async def test_stop_watchdog(controller, uuid4, mock_command):
    """Test stop_watchdog command."""
    ack_commands = mock_command(
        {"command": "controller.stop_watchdog"},
        {"success": True},
    )

    result = await controller.async_stop_watchdog()
    assert result is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.stop_watchdog",
        "messageId": uuid4,
    }


async def test_get_supported_rf_regions(controller, uuid4, mock_command):
    """Test get_supported_rf_regions command."""
    ack_commands = mock_command(
        {"command": "controller.get_supported_rf_regions"},
        {"regions": [0, 1, 2]},
    )

    result = await controller.async_get_supported_rf_regions()
    assert result == [
        RFRegion.EUROPE,
        RFRegion.USA,
        RFRegion.AUSTRALIA_AND_NEW_ZEALAND,
    ]

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.get_supported_rf_regions",
        "filterSubsets": False,
        "messageId": uuid4,
    }


async def test_query_supported_rf_regions(controller, uuid4, mock_command):
    """Test query_supported_rf_regions command."""
    ack_commands = mock_command(
        {"command": "controller.query_supported_rf_regions"},
        {"regions": [0, 1]},
    )

    result = await controller.async_query_supported_rf_regions()
    assert result == [RFRegion.EUROPE, RFRegion.USA]

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.query_supported_rf_regions",
        "messageId": uuid4,
    }


async def test_query_rf_region_info(controller, uuid4, mock_command):
    """Test query_rf_region_info command."""
    ack_commands = mock_command(
        {"command": "controller.query_rf_region_info"},
        {
            "region": 1,
            "supportsZWave": True,
            "supportsLongRange": True,
        },
    )

    result = await controller.async_query_rf_region_info(RFRegion.USA)
    assert result["region"] == 1
    assert result["supportsZWave"] is True
    assert result["supportsLongRange"] is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.query_rf_region_info",
        "region": RFRegion.USA.value,
        "messageId": uuid4,
    }


async def test_assign_return_routes(
    controller, multisensor_6, lock_schlage_be469, uuid4, mock_command
):
    """Test assign_return_routes command."""
    ack_commands = mock_command(
        {"command": "controller.assign_return_routes"},
        {"success": True},
    )

    result = await controller.async_assign_return_routes(
        multisensor_6, lock_schlage_be469
    )
    assert result is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.assign_return_routes",
        "nodeId": multisensor_6.node_id,
        "destinationNodeId": lock_schlage_be469.node_id,
        "messageId": uuid4,
    }


async def test_delete_return_routes(controller, multisensor_6, uuid4, mock_command):
    """Test delete_return_routes command."""
    ack_commands = mock_command(
        {"command": "controller.delete_return_routes"},
        {"success": True},
    )

    result = await controller.async_delete_return_routes(multisensor_6)
    assert result is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.delete_return_routes",
        "nodeId": multisensor_6.node_id,
        "messageId": uuid4,
    }


async def test_assign_suc_return_routes(controller, multisensor_6, uuid4, mock_command):
    """Test assign_suc_return_routes command."""
    ack_commands = mock_command(
        {"command": "controller.assign_suc_return_routes"},
        {"success": True},
    )

    result = await controller.async_assign_suc_return_routes(multisensor_6)
    assert result is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.assign_suc_return_routes",
        "nodeId": multisensor_6.node_id,
        "messageId": uuid4,
    }


async def test_delete_suc_return_routes(controller, multisensor_6, uuid4, mock_command):
    """Test delete_suc_return_routes command."""
    ack_commands = mock_command(
        {"command": "controller.delete_suc_return_routes"},
        {"success": True},
    )

    result = await controller.async_delete_suc_return_routes(multisensor_6)
    assert result is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.delete_suc_return_routes",
        "nodeId": multisensor_6.node_id,
        "messageId": uuid4,
    }


async def test_discover_node_neighbors(controller, multisensor_6, uuid4, mock_command):
    """Test discover_node_neighbors command."""
    ack_commands = mock_command(
        {"command": "controller.discover_node_neighbors"},
        {"success": True},
    )

    result = await controller.async_discover_node_neighbors(multisensor_6)
    assert result is True

    assert len(ack_commands) == 1
    assert ack_commands[0] == {
        "command": "controller.discover_node_neighbors",
        "nodeId": multisensor_6.node_id,
        "messageId": uuid4,
    }


async def test_controller_state_properties_schema_45(controller_state):
    """Test controller state properties from schema 45."""
    state = deepcopy(controller_state)
    state["controller"]["isSIS"] = True
    state["controller"]["maxPayloadSize"] = 48
    state["controller"]["maxPayloadSizeLR"] = 96
    state["controller"]["zwaveApiVersion"] = {"kind": 1, "version": "1.2.3"}
    state["controller"]["zwaveChipType"] = {"type": 7, "version": 1}

    ctrl = controller_pkg.Controller(None, state)

    assert ctrl.is_sis is True
    assert ctrl.max_payload_size == 48
    assert ctrl.max_payload_size_lr == 96
    assert ctrl.zwave_api_version == {"kind": 1, "version": "1.2.3"}
    assert ctrl.zwave_chip_type == {"type": 7, "version": 1}


async def test_controller_state_properties_schema_45_missing(controller_state):
    """Test controller state properties from schema 45 when not present."""
    ctrl = controller_pkg.Controller(None, controller_state)

    assert ctrl.is_sis is None
    assert ctrl.max_payload_size is None
    assert ctrl.max_payload_size_lr is None
    assert ctrl.zwave_api_version is None
    assert ctrl.zwave_chip_type is None


async def test_network_events(controller):
    """Test network-related events from schema 45."""
    # Test network found event
    event = Event(
        "network found",
        {
            "source": "controller",
            "event": "network found",
            "homeId": 12345678,
            "ownNodeId": 1,
        },
    )
    controller.receive_event(event)
    assert event.data["homeId"] == 12345678
    assert event.data["ownNodeId"] == 1

    # Test network joined event
    event = Event(
        "network joined",
        {"source": "controller", "event": "network joined"},
    )
    controller.receive_event(event)

    # Test network left event
    event = Event(
        "network left",
        {"source": "controller", "event": "network left"},
    )
    controller.receive_event(event)

    # Test joining network failed event
    event = Event(
        "joining network failed",
        {"source": "controller", "event": "joining network failed"},
    )
    controller.receive_event(event)

    # Test leaving network failed event
    event = Event(
        "leaving network failed",
        {"source": "controller", "event": "leaving network failed"},
    )
    controller.receive_event(event)
