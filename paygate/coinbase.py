import requests
import json

API_KEY = '6e6cd68f-896a-4156-9995-7c64c6f71bcf'

url = 'https://api.commerce.coinbase.com/checkouts'
urlc = 'https://api.commerce.coinbase.com/charges'
headers = {'X-CC-Api-Key': API_KEY, 'X-CC-Version':'2018-03-22'}


req = requests.get(urlc, headers=headers)

print(json.loads(req.text))