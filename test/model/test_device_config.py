"""Test the device config model."""
import json

from zwave_js_server.model.device_config import DeviceConfig

from .. import load_fixture


async def test_device_config():
    """Test a device config."""
    device_config = DeviceConfig(
        json.loads(load_fixture("vision_security_zse40_device_config.json"))
    )
    assert device_config.is_embedded
    assert device_config.filename == (
        "/opt/node_modules/@zwave-js/config/config/devices/0x0109/zse40.json"
    )
    assert device_config.manufacturer == "Vision Security"
    assert device_config.manufacturer_id == 265
    assert device_config.label == "ZSE40"
    assert device_config.description == (
        "Zooz 4-in-one motion/temperature/humidity/luminance sensor"
    )
    assert len(device_config.devices) == 1
    assert device_config.devices[0].product_id == 8449
    assert device_config.devices[0].product_type == 8225
    assert device_config.firmware_version.min == "0.0"
    assert device_config.firmware_version.max == "255.255"
    assert device_config.metadata.inclusion == (
        "To add the ZP3111 to the Z-Wave network (inclusion), place the Z-Wave "
        "primary controller into inclusion mode. Press the Program Switch of ZP3111 "
        "for sending the NIF. After sending NIF, Z-Wave will send the auto inclusion, "
        "otherwise, ZP3111 will go to sleep after 20 seconds."
    )
    assert device_config.metadata.exclusion == (
        "To remove the ZP3111 from the Z-Wave network (exclusion), place the Z-Wave "
        "primary controller into \u201cexclusion\u201d mode, and following its "
        "instruction to delete the ZP3111 to the controller. Press the Program Switch "
        "of ZP3111 once to be excluded."
    )
    assert device_config.metadata.reset == (
        "Remove cover to trigged tamper switch, LED flash once & send out Alarm "
        "Report. Press Program Switch 10 times within 10 seconds, ZP3111 will send "
        "the \u201cDevice Reset Locally Notification\u201d command and reset to the "
        "factory default. (Remark: This is to be used only in the case of primary "
        "controller being inoperable or otherwise unavailable.)"
    )
    assert device_config.metadata.manual == (
        "https://products.z-wavealliance.org/ProductManual/File?folder=&filename=MarketCertificationFiles/2479/ZP3111-5_R2_20170316.pdf"
    )
    assert device_config.metadata.wakeup is None
    assert device_config.associations == {}
    assert device_config.param_information == {"_map": {}}
