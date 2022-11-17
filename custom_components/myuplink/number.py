"""
Number devices from myUplink API
For more details about this platform, please refer to the documentation at 
https://github.com/kayjei/homeassistant-myuplink

For API documentation, refer to https://dev.myuplink.com/ and swagger https://api.myuplink.com/swagger/index.html
"""
import logging
import sys
import time
import requests
import json
import datetime
import voluptuous as vol
from .connect import myUplink
from typing import Any, final

import homeassistant.helpers.config_validation as cv

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.helpers.typing import ConfigType
from . import DOMAIN
from homeassistant.core import HomeAssistant

from homeassistant.components.number.const import (ATTR_MAX, ATTR_MIN, ATTR_STEP)
from homeassistant.const import ATTR_MODE
from homeassistant.backports.enum import StrEnum

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = datetime.timedelta(minutes=3)

class NumberMode(StrEnum):
    """Modes for number entities."""

    AUTO = "auto"
    BOX = "box"
    SLIDER = "slider"

def setup_platform(hass: HomeAssistant, config: ConfigType, add_entities, discovery_info=None):
    """Set up the myuplink number sensor."""

    _LOGGER.debug("Adding number component: myUplink ... %s", hass.data[DOMAIN])
    config.update({ 'api_key': hass.data[DOMAIN]['api_key'], 'api_token': hass.data[DOMAIN]['api_token'], 'region': hass.data[DOMAIN]['region'] })

    devices = []
    valid_devices = ['61503']

    systems = myUplink.do_get_systems(config)
    for system in systems["systems"]:
        _LOGGER.debug("Trying system: %s", str(system))

        for device in system["devices"]:
            _LOGGER.debug("Trying device: %s", str(device))
            device_data = myUplink.do_get_sensors(device["id"], config)

            for sensor in device_data:
                if sensor["parameterId"] in valid_devices:
                    devices.append(uplinkDevice(config, device["id"], device["product"]["name"], sensor["parameterId"], sensor["parameterName"], sensor["parameterUnit"], sensor["value"], sensor["minValue"], sensor["maxValue"], sensor["scaleValue"]))

    add_entities(devices, True)


class uplinkDevice(NumberEntity):
    """Representation of a number."""

    def __init__(self, config, device_id, device_name, sensor_id, name, unit, value, minval, maxval, scalevalue):
        """Initialize the number device."""
        self._device_id = device_id
        self._device_name = device_name
        self._sensor_id = sensor_id
        self._entity_id = f"number.{self._device_id.lower()}_{self._sensor_id.lower()}"
        self._name = name
        self._unit = unit
        self._state = value
        #self._max_value = maxval #Scale value is 0.5 according to the API, but returns faulty values in the heater
        self._max_value = 10 
        self._min_value = minval
        #self._scale_value = scalevalue #Scale value is 0.5 according to the API, but returns faulty values in the heater
        self._scale_value = 1
        self._config = config
        self._mode = 'slider'
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
        """Return the name of the device"""
        return self._entity_id

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit

    @property
    def mode(self) -> NumberMode:
        """Return the mode of the entity."""
        return self._mode

    @property
    def name(self):
        """Return the name of the device, if any."""
        return self._name

    @property
    def should_poll(self):
        """Polling is required."""
        return True

    @property
    def capability_attributes(self) -> dict[str, Any]:
        """Return capability attributes."""
        return {
            ATTR_MIN: self._min_value,
            ATTR_MAX: self._max_value,
            ATTR_STEP: self._scale_value,
            ATTR_MODE: self._mode,
        }

    @property
    def native_min_value(self):
        """Return the minimum temperature."""
        return self._min_value

    @property
    def native_max_value(self):
        """Return the maximum temperature."""
        return self._max_value

    @property
    def native_step(self):
        """Return the maximum temperature."""
        return self._scale_value

    @property
    def native_value(self):
        """Return the current temperature."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the attribute(s) of the sensor"""
        return {
            "device": self._device_name
        }

    def set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._state = value
        send_value = int(value)
        myUplink.do_patch_sensor(self._device_id, self._sensor_id, send_value, self._config)
