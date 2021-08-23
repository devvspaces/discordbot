import time

from django.http import JsonResponse

class AjaxResponders(object):
    def json_err_response(self, response):
        message = 'Problem connecting with server, try again in a few mins'
        if isinstance(response, str):
            # This means a message was passed
            message = response
        
        time.sleep(3)
        return JsonResponse({'data': 'invalid', 'message': message }, status=400)