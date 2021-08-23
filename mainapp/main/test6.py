import uuid
import requests
import json

g = uuid.uuid4()
print(g)
body = {
    "name":       "AftonFin",
    "password":   "@Afton7&@",
    # "appId":      "AftonDEMO",
    # "appVersion": "0.0.1",
    # "cid":        59,
    # "sec":        "30b2bee4-9a61-4ca2-ae38-f8b0b9ab1954",
    # "deviceId":   "0a401aae-6859-26e9-e7d8-f2971395d20c"
}

headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

response = requests.post(url='https://demo.tradovateapi.com/v1/auth/accesstokenrequest', data=json.dumps(body), headers=headers, verify=True)
print(response.status_code)
print(response.content)
print(response.text)

# response = requests.post(url='http://www.wellbos.com')
# print(response.content)




REDIRECT_URI  = 'http://localhost:3030/oauth/tradovate/callback'
EXCHANGE_URL  = 'https://live-d.tradovateapi.com/auth/oauthtoken'
AUTH_URL      = 'https://trader-d.tradovate.com/oauth'

'https://trader-d.tradovate.com/oauth?response_type=code&client_id=59&redirect_uri=http://www.wellbos.com'