# homeassistant-myuplink
Homeassistant integration for sensors in myUplink account

1. Create a dev account on https://dev.myuplink.com/
2. Create API credentials by creating a new application. Callback URL will not be nescessary.
3. Download this integration in HACS
4. Add you credentials in configuration.yaml
```
myuplink:
  api_key: CLIENT_IDENTIFIER 
  api_token: CLIENT_SECRET
  region: sv-SE
```
Region is optional and shall in be the Accept-Language header format. Supported languages is documented under Language in https://dev.myuplink.com/
