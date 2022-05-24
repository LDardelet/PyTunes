import requests
import json

from .tools import AutoConfig

"""Remote library communication handler.
"""
class DjangoClientC(AutoConfig):
    ConfigKey = 'client'
    Params = [('adress', 'localhost'),
              ('port', 8000),]

    HEADERS = {
        'content-type': "application/json",
        'cache-control': "no-cache",
    }
    def __init__(self, config):
        self.UpdateParams(config)

    @property
    def Url(self):
        return f"http://{self.ADRESS}:{self.PORT}"
    
    def get(self, suffix='', payload=None):
        if suffix[0] != '/':
            suffix = '/'+suffix
        if payload is None:
            payload = {}
        return requests.get(self.Url+suffix, data=json.dumps(payload), headers=self.HEADERS)

    def post(self, suffix='', payload=None):
        if suffix[0] != '/':
            suffix = '/'+suffix
        if payload is None:
            payload = {}
        return requests.post(self.Url+suffix, data=json.dumps(payload), headers=self.HEADERS)

    def delete(self, suffix='', payload=None):
        if suffix[0] != '/':
            suffix = '/'+suffix
        if payload is None:
            payload = {}
        return requests.delete(self.Url+suffix, data=json.dumps(payload), headers=self.HEADERS)
