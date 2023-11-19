from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import pandas as pd
import time

import sys
sys.path.append('../')
from onemap_client import OneMapClient
import os
from dotenv import load_dotenv
load_dotenv()
tqdm.pandas()

import asyncio
import aiohttp


email = os.environ['ONE_MAP_API_EMAIL']
password = os.environ['ONE_MAP_API_PASSWORD']

async def main():
   
    with open('./search/one_map_search_phrase.json', 'r') as f:
        addresses = json.load(f)

    client = OneMapClient(email, password)
    async with aiohttp.ClientSession() as session:
        tasks = [client.async_search(address, session, return_geom=True, get_addr_details=True, page_num=1) for address in addresses]
        responses = await asyncio.gather(*tasks)

        if os.path.exists('./search/one_map_search_results_db.json'):
            with open('./search/one_map_search_results_db.json', 'r') as f:
                db_results = json.load(f)
        else:
            db_results = {}
        
        for resp in responses:
            if resp!=None and 'error' not in resp and resp['found']>0:
                db_results[resp['search_phrase']] = resp['results']
        
        with open('./search/one_map_search_results_db.json', 'w') as f:
            json.dump(db_results, f)
        
        os.remove('./search/one_map_search_phrase.json')
    

if __name__=='__main__':
    asyncio.run(main())       