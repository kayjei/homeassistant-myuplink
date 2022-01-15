"""Connect API parameters for myUplink"""
import logging
import requests
import json
import time

_LOGGER = logging.getLogger(__name__)

url = 'https://api.myuplink.com'

class myUplink:

    @staticmethod
    def do_get_sensors(device_id, config):
        """API request to fetch all sensors on a device"""

        myUplink.authenticate(config)

        headers = { "Accept": "text/plain", "Accept-Language": config["region"], "Authorization": "Bearer " + config["token"] }

        req = requests.get(url + '/v2/devices/' + str(device_id) + '/points', headers=headers)

        if req.status_code != requests.codes.ok:
            _LOGGER.exception("API request returned error %s", req.status_code)
        else:
            _LOGGER.debug("API request returned OK %s", req.text)

        json_data = json.loads(req.content)
        return json_data

    @staticmethod
    def do_get_single_sensor(device_id, sensor_id, config):
        """API request to fetch a single sensor"""

        myUplink.authenticate(config)

        headers = { "Accept": "text/plain", "Accept-Language": config["region"], "Authorization": "Bearer " + config["token"] }

        req = requests.get(url + '/v2/devices/' + str(device_id) + '/points?parameters=' + str(sensor_id), headers=headers)

        if req.status_code != requests.codes.ok:
            _LOGGER.exception("API request returned error %s", req.status_code)
        else:
            _LOGGER.debug("API request returned OK %s", req.text)

        json_data = json.loads(req.content)
        return json_data

    @staticmethod
    def do_get_systems(config):
        """API request to fetch all devices on a system"""
        
        myUplink.authenticate(config)
        
        headers = { "Accept": "text/plain", "Authorization": "Bearer " + config["token"] }

        req = requests.get(url + '/v2/systems/me', headers=headers)

        if req.status_code != requests.codes.ok:
            _LOGGER.exception("API request returned error %s", req.status_code)
        else:
            _LOGGER.debug("API request returned OK %s", req.text)

        json_data = json.loads(req.content)
        return json_data

    @staticmethod
    def authenticate(config):
        """Authentication flow and API request"""
        headers = { "Content-Type": "application/x-www-form-urlencoded" }
        parameters = { "grant_type": "client_credentials", "client_id": config["api_key"], "client_secret": config["api_token"], "scope": "READSYSTEM" }

        if "token" not in config:
            req = requests.post(url + '/oauth/token', headers=headers, data=parameters)

            if req.status_code != requests.codes.ok:
                _LOGGER.exception("API request returned error %s", req.status_code)
            else:
                _LOGGER.debug("API request returned OK %s", req.text)
                json_data = json.loads(req.content)
                config.update({ "token": json_data["access_token"], "expire": int(time.time()) + int(json_data["expires_in"]) })
                
        else:
            if time.time() + 30 > config["expire"]:
                req = requests.post(url + '/oauth/token', headers=headers, data=parameters)

                if req.status_code != requests.codes.ok:
                    _LOGGER.exception("API request returned error %s", req.status_code)
                else:
                    _LOGGER.debug("API request returned OK %s", req.text)
                    json_data = json.loads(req.content)
                    config.update({ "token": json_data["access_token"], "expire": int(time.time()) + int(json_data["expires_in"]) })

            else:
                config.update({ "token": config["token"], "expire": config["expire"] })
        
        
        return True
