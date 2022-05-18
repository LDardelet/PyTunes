import requests
import json

class Handler:
    HEADERS = {
        'content-type': "application/json",
        'cache-control': "no-cache",
    }

    def __init__(self, config):
        self.ADRESS = config.get('adress', 'localhost')
        self.PORT = config.get('port', 8000)

    @property
    def Url(self):
        return f"http://{self.ADRESS}:{self.PORT}"
    
    def get(self, suff='', payload=None):
        if suff[0] != '/':
            suff = '/'+suff
        if payload is None:
            payload = {}
        return requests.get(self.Url+suff, data=json.dumps(payload), headers=self.HEADERS)
