"""
A sensor created to read temperature from myUplink public API
For more details about this platform, please refer to the documentation at
https://github.com/kayjei/homeassistant-myuplink

For API documentation, refer to https://dev.myuplink.com/ and swagger https://api.myuplink.com/swagger/index.html
"""

import logging
import voluptuous as vol
import datetime
from .connect import myUplink

from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.util import Throttle
from homeassistant.const import (TEMP_CELSIUS, CONF_API_KEY, CONF_API_TOKEN, CONF_REGION)

DOMAIN = "myuplink"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_API_TOKEN): cv.string,
    vol.Optional(CONF_REGION, default="en-US"): cv.string
})

UPDATE_INTERVAL = datetime.timedelta(minutes=3)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform"""
    _LOGGER.debug("Adding sensor component: myUplink ...")
    devices = []
    valid_devices = ['62006','62000','62011','62015','62027','62037','62168','62169','62171','62172','62173','62276']

    systems = myUplink.do_get_systems(config)
    for system in systems["systems"]:
        _LOGGER.debug("Trying system: %s", str(system))

        for device in system["devices"]:
            _LOGGER.debug("Trying device: %s", str(device))
            device_data = myUplink.do_get_sensors(device["id"], config)

            for sensor in device_data:
                if sensor["parameterId"] in valid_devices:
                    devices.append(myUplinkSensor(config, device["id"], device["product"]["name"], sensor["parameterId"], sensor["parameterName"], sensor["parameterUnit"], sensor["value"]))

    add_entities(devices, True)

class myUplinkSensor(Entity):
    def __init__(self, config, device_id, device_name, sensor_id, name, unit, value):
        self._device_id = device_id
        self._device_name = device_name
        self._sensor_id = sensor_id
        self._entity_id = "sensor." + str(self._device_id).lower() + '_' + str(self._sensor_id).lower()
        self._name = name
        self._unit = unit
        self._state = value
        self._config = config
        self.update()

    @Throttle(UPDATE_INTERVAL)
    def update(self):
        """Sensors"""

        device_data = myUplink.do_get_single_sensor(str(self._device_id), str(self._sensor_id), self._config)
        for device in device_data:
            self._name = device["parameterName"]
            self._unit = device["parameterUnit"]
            self._state = device["value"]

    @property
    def entity_id(self):
        """Return the id of the sensor"""
        return self._entity_id

    @property
    def name(self):
        """Return the name of the sensor"""
        return self._name

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def state(self):
        """Return the state of the sensor"""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the attribute(s) of the sensor"""
        return {
            "device": self._device_name
        }
