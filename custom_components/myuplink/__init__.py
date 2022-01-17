"""Integration for MyUplink."""
import logging
import sys
import voluptuous as vol
from .connect import myUplink

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_API_KEY, CONF_API_TOKEN, CONF_REGION)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType


PLATFORMS = [Platform.CLIMATE, Platform.SENSOR, Platform.NUMBER]

DOMAIN = "myuplink"

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
  DOMAIN: {
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_API_TOKEN): cv.string,
    vol.Optional(CONF_REGION, default="en-US"): cv.string
  },
}, extra=vol.ALLOW_EXTRA)

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Share data and load platforms."""
    
    _LOGGER.debug("Initializing component: myUplink ...")

    hass.data[DOMAIN] = {
        'api_key': config[DOMAIN]['api_key'],
        'api_token': config[DOMAIN]['api_token'],
        'region': config[DOMAIN]['region']
    }

    if DOMAIN not in config:
        return True
  
    myUplink.authenticate(config[DOMAIN])
    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('number', DOMAIN, {}, config)

    return True
