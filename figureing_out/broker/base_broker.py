import requests
import json

class BaseBroker:

    def __init__(self):
        self.base_url = ''
        
    def _get_headers(self):
        raise NotImplementedError("This method must be overridden by the subclass.")

    def _make_request(self, endpoint, method="GET", params=None):
        '''
        only GET and POST request supported
        '''
        url = self.base_url + endpoint
        headers = self._get_headers()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=params)
            else:
                raise ValueError("Unsupported HTTP method")
            
            response.raise_for_status()
            return self._format_response(success = True, data = response.json())
        
        except requests.exceptions.HTTPError as http_err:
            return {"error": f"HTTP error occurred: {http_err}"}
        except Exception as err:
            return {"error": f"Other error occurred: {err}"}
        
    def _format_response(self, success, message = None, data=None):
        try:
            response = {'success': success}
            if message:
                response['message'] = message
            if data:
                response['data'] = data
            return response
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response"}

    def get_account_info(self):
        raise NotImplementedError("This method must be overridden by the subclass.")
    
    def place_order(self, symbol, side, quantity, price=None):
        raise NotImplementedError("This method must be overridden by the subclass.")
    
    def get_order_status(self, order_id):
        raise NotImplementedError("This method must be overridden by the subclass.")
