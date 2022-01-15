# homeassistant-myuplink
Homeassistant integration for sensors in myUplink account

1. Create a dev account on https://dev.myuplink.com/
2. Create API credentials
3. Download this integration in HACS
4. Add you credentials
```
sensor:
  - platform: myuplink
    api_key: YOUR_API_KEY
    api_token: YOUR_API_TOKEN
    region: se-SV
```
Region is optional and shall in be the Accept-Language header format. Supported languages is documented under Language in https://dev.myuplink.com/
