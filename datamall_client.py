from requests_toolbelt.multipart.encoder import MultipartEncoder
import time
import requests
import json

class DataMallClient():
    def __init__(self,api_key):
        self.api_key = api_key
        self.base_url = 'http://datamall2.mytransport.sg/ltaodataservice'
        self.header = {'AccountKey':self.api_key,
                       'accept':'application/json'}
    
    def retrieve_bus_stops(self,skip=0):

        try:
            response = requests.get(self.base_url+f'/BusStops?$skip={skip}',
                                    headers=self.header).text
            return json.loads(response)
        except Exception as e:
            print(e)
            return
        
