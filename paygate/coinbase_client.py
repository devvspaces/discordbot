import  requests
import json

from django.conf import settings
from django.urls import reverse

from .models import Order
from .utils import build_uri

'''
This file contains the coinbase client i personally build to be a connection to coinbase commerce api
'''

# Our custom exceptions
class BadCoinbaseRequest(Exception):
    def __init__(self, error_body=None, message='Request to api returned as bad request'):
        if error_body is not None:
            message = f"Type: {error_body['error']['type']} : {error_body['error']['message']}"
        
        self.message = message
        super().__init__(self.message)

class CommonError(Exception):
    pass

class CoinbaseClient:
    def __init__(self):
        self.api_key = settings.COINBASE_API_KEY
        self.version = settings.COINBASE_API_VERSION
        self.base_url = 'https://api.commerce.coinbase.com'
        self.headers = {'X-CC-Api-Key': self.api_key, 'X-CC-Version':self.version}

        self.checkout_base = '/checkouts'
        self.charge_base = '/charges'
    
    def get_response(self, url=''):
        response = requests.get(self.base_url + url, headers=self.headers)
        if response.status_code == 200:
            return json.loads(response.content.decode())
        elif (response.status_code == 400) or (response.status_code == 429):
            raise BadCoinbaseRequest(error_body=json.loads(response.text))
        
        raise CommonError(f'Status code:{response.status_code} : Request is not processed')
    
    def post_response(self, url='', data=None):
        if data is None:
            data = {}

        response = requests.get(self.base_url + url, headers=self.headers, data=data)
        if response.status_code == 200:
            return json.loads(response.content.decode())
        elif (response.status_code == 400) or (response.status_code == 429):
            raise BadCoinbaseRequest(error_body=json.loads(response.text))

        print(response.content, response.status_code)
        
        raise CommonError(f'Status code:{response.status_code} : Request is not processed')

    def list_checkout(self):
        return self.get_response(url=self.checkout_base)['data']
    
    def get_checkout(self, checkout_id):
        return self.get_response(url=f'{self.checkout_base}/{checkout_id}')
    
    def get_checkout_link(self, checkout_id):
        return f"https://commerce.coinbase.com/checkout/{checkout_id}"
    
    # def create_checkout(self, package):
    #     body = {
    #         "name": f"{package.amount} Messages",
    #         "description": package.description,
    #         "local_price": {
    #             "amount": package.price,
    #             "currency": "USD"
    #         },
    #         "pricing_type": "fixed_price",
    #         "requested_info": ["email"]
    #     }

    #     # Make request
    #     response = self.post_response(url=self.charge_base, data=body)
    #     print(response)

    #     return response['data'][0]
    
    def create_charge(self, checkout_id, user, request): 
        checkout_response = self.get_checkout(checkout_id)['data']

        # body = {
        #     "name": checkout_response['name'],
        #     "description": checkout_response['description'],
        #     "local_price": {
        #         "amount": checkout_response['local_price']['amount'],
        #         "currency": checkout_response['local_price']['currency']
        #     },
        #     "pricing_type": checkout_response['pricing_type'],
        #     "metadata": {
        #         "customer_id": user.profile.uid,
        #         "customer_name": user.email
        #     },
        #     "redirect_url": build_uri(reverse('dashboard:home'), request),
        #     "cancel_url": build_uri(reverse('dashboard:packages'), request)
        # }

        # # Make request
        # response = self.post_response(url=self.charge_base, data=body)
        # data = response.get('data')[0]

        # Get charge details from returned data
        # order_id = data.get('id')
        # name = data.get('name')
        # charge_url = data.get('hosted_url')
        dm_amount = float(checkout_response['name'].split(' ')[0].replace(',',''))

        # Create new order
        order = Order.objects.create(profile=user.profile, dm_amount=dm_amount)

        # Return charge url
        return self.get_checkout_link(checkout_id)

    



coinbase_api = CoinbaseClient()


"""
For checkout id creating charge
def create_charge(self, checkout_id, user): 
        checkout_response = self.get_checkout(checkout_id)
        body = {
            "name": checkout_response['name'],
            "description": checkout_response['description'],
            "local_price": {
                "amount": checkout_response['local_price']['amount'],
                "currency": checkout_response['local_price']['currency']
            },
            "pricing_type": checkout_response['pricing_type'],
            "metadata": {
                "customer_id": user.profile.uid,
                "customer_name": user.email
            },
            "redirect_url": build_uri(reverse('dashboard:home')),
            "cancel_url": build_uri(reverse('dashboard:packages'))
        }

        # Make request
        response = self.post_response(url=self.charge_base, data=body)
        data = response.get('data')

        # Get charge details from returned data
        order_id = data.get('id')
        name = data.get('name')
        charge_url = data.get('hosted_url')
        dm_amount = float(name.split(' ')[0].replace(',',''))

        # Create new order
        order = Order.objects.create(order_id=order_id, profile=user.profile, dm_amount=dm_amount)

        # Return charge url
        return charge_url
"""


"""
def create_charge(self, package, user, request):
        print(self.list_checkout())
        self.create_checkout(package)

        body = {
            "name": f"{package.amount} Messages",
            "description": package.description,
            "local_price": {
                "amount": package.price,
                "currency": "USD"
            },
            "pricing_type": "fixed_price",
            "metadata": {
                "customer_id": user.profile.uid,
                "customer_name": user.email
            },
            "redirect_url": build_uri(reverse('dashboard:home'), request),
            "cancel_url": build_uri(reverse('dashboard:packages'), request)
        }

        # Make request
        response = self.post_response(url=self.charge_base, data=body)
        print(response)
        data = response.get('data')[0]

        # Get charge details from returned data
        order_id = data.get('id')
        name = data.get('name')
        charge_url = data.get('hosted_url')
        dm_amount = float(name.split(' ')[0])

        # Create new order
        querysets = Order.objects.filter(order_id__exact=order_id)
        if querysets.exists():
            print(querysets)
            return charge_url
        order = Order.objects.create(order_id=order_id, profile=user.profile, dm_amount=dm_amount)

        # Return charge url
        return charge_url
"""