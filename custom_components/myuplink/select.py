"""
Number devices from myUplink API
For more details about this platform, please refer to the documentation at
https://github.com/kayjei/homeassistant-myuplink

For API documentation, refer to https://dev.myuplink.com/ and swagger https://api.myuplink.com/swagger/index.html
"""
import logging
import datetime

from .connect import myUplink

from homeassistant.components.select import SelectEntity
#from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.helpers.typing import ConfigType
from . import DOMAIN
from homeassistant.core import HomeAssistant

#from homeassistant.const import ATTR_MODE
#from homeassistant.backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = datetime.timedelta(minutes=3)


def setup_platform(hass: HomeAssistant, config: ConfigType, add_entities, discovery_info=None):
    """Set up the myuplink selector."""

    _LOGGER.debug("Adding select component: myUplink ... %s", hass.data[DOMAIN])
    config.update({ 'api_key': hass.data[DOMAIN]['api_key'], 'api_token': hass.data[DOMAIN]['api_token'], 'region': hass.data[DOMAIN]['region'] })

    devices = []
    enums = []
    valid_devices = ['1005']

    systems = myUplink.do_get_systems(config)
    for system in systems["systems"]:
        _LOGGER.debug("Trying system: %s", str(system))

        for device in system["devices"]:
            _LOGGER.debug("Trying device: %s", str(device))
            device_data = myUplink.do_get_sensors(device["id"], config)

            for sensor in device_data:
                if sensor["parameterId"] in valid_devices:
                    for enum in sensor["enumValues"]:
                        enums.append({"value": enum["value"], "text": enum["text"]})
                    devices.append(
                        uplinkDevice(
                            config,
                            device["id"],
                            device["product"]["name"],
                            sensor["parameterId"],
                            sensor["parameterName"],
                            sensor["value"],
                            enums
                        )
                    )

    add_entities(devices, True)


class uplinkDevice(SelectEntity):
    """Representation of a select."""

    def __init__(self, config, device_id, device_name, sensor_id, name, value, enums):
        """Initialize the number device."""
        self._device_id = device_id
        self._device_name = device_name
        self._sensor_id = sensor_id
        self._entity_id = "select." + str(self._device_id).lower() + '_' + str(self._sensor_id).lower()
        self._name = name
        self._state = value
        self._config = config
        self._enums = enums
        self.update()

    @Throttle(UPDATE_INTERVAL)
    def update(self):
        """Sensors"""

        device_data = myUplink.do_get_single_sensor(str(self._device_id), str(self._sensor_id), self._config)
        for device in device_data:
            self._name = device["parameterName"]
            self._state = device["value"]

    @property
    def entity_id(self):
        """Return the name of the device"""
        return self._entity_id

    @property
    def name(self):
        """Return the name of the device, if any."""
        return self._name

    @property
    def should_poll(self):
        """Polling is required."""
        return True

    @property
    def select_option(selfself):
        """Return available options"""
        options = []
        for i in self._enums:
            options.append(i["value"])
        return options

    @property
    def current_option(self):
        """Return the current option."""
        return self._state

    def set_value(self, value: float) -> None:
        """Update the current value."""
        self._state = value
        send_value = int(value)
        myUplink.do_patch_sensor(self._device_id, self._sensor_id, send_value, self._config)
