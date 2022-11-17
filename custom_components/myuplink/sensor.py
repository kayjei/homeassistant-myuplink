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
from homeassistant.util import Throttle
from homeassistant.helpers.typing import ConfigType
from . import DOMAIN
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = datetime.timedelta(minutes=3)

def setup_platform(hass: HomeAssistant, config: ConfigType, add_entities, discovery_info=None):
    """Set up the sensor platform"""
    _LOGGER.debug("Adding sensor component: myUplink ...")
    config.update({ 'api_key': hass.data[DOMAIN]['api_key'], 'api_token': hass.data[DOMAIN]['api_token'], 'region': hass.data[DOMAIN]['region'] })

    devices = []
    valid_devices = ['62006','62000','62011','62015','62027','62037','62168','62169','62171','62172','62173','62276','62107','62147']

    systems = myUplink.do_get_systems(config)
    for system in systems["systems"]:
        _LOGGER.debug("Trying system: %s", str(system))

        for device in system["devices"]:
            _LOGGER.debug("Trying device: %s", str(device))
            device_data = myUplink.do_get_sensors(device["id"], config)

            for sensor in device_data:
                if sensor["parameterId"] in valid_devices:
                    if sensor["parameterUnit"] in ['kW', 'A']:
                        icon = 'mdi:lightning-bolt'
                    elif sensor["parameterUnit"] in ['°C']:
                        icon = 'mdi:temperature-celsius'
                    else:
                        icon = ''
                    update_interval = datetime.timedelta(minutes=3)

                    devices.append(myUplinkSensor(config, device["id"], device["product"]["name"], sensor["parameterId"], sensor["parameterName"], sensor["parameterUnit"], icon, sensor["value"]))

    add_entities(devices, True)

class myUplinkSensor(Entity):

    def __init__(self, config, device_id, device_name, sensor_id, name, unit, icon, value):
        self._device_id = device_id
        self._device_name = device_name
        self._sensor_id = sensor_id
        self._entity_id = f"sensor.{self._device_id.lower()}_{self._sensor_id.lower()}"
        self._name = name
        self._unit = unit
        self._state = value
        self._icon = icon
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
    def unique_id(self):
        """Return the id of the sensor"""
        return self._entity_id

    @property
    def name(self):
        """Return the name of the sensor"""
        return self._name

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def device_class(self):
        if self._unit == '°C' or self._unit == '°F':
            return 'temperature'
        elif self._unit == 'A':
            return 'current'
        elif self._unit == 'kW':
            return 'power'

    @property
    def state_class(self):
        return 'measurement'

    @property
    def state(self):
        """Return the state of the sensor"""
        return self._state

    @property
    def native_value(self):
        """Return the state of the sensor"""
        return self._state

    @property
    def icon(self):
        """Return the state of the sensor"""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the attribute(s) of the sensor"""
        return {
            "device": self._device_name
        }