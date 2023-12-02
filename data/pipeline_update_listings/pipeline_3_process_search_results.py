
import json
from tqdm import tqdm
import pandas as pd
import re

import sys
sys.path.append('../../')
from data.pipeline_update_listings.pipeline_3_process_address import onemap_search_addresses

import os
from dotenv import load_dotenv
import asyncio
load_dotenv()
tqdm.pandas()


def process_search_results(input_file, output_file, onemap_search_db=None):
    with open(input_file, 'r') as f:
        store = json.load(f)

    store_df = {
        'id': [],
        'name': [], 
        'url': [], 
        'street_address': [], 
        'price': [], 
        'num_bedroom': [], 
        'num_bathroom': [], 
        'cost_psf': [], 
        'total_area': [],
        'walk': [],
        'tags': [],
        'recency': [],
    }
    for key, value in store.items():
        store_df['id'].append(key)
        for i, j in value.items():
            store_df[i].append(j)

    listings = pd.DataFrame(store_df)

    for i, row in tqdm(listings.iterrows()):
        listings.at[i, 'name'] = clean_name(row['name'])
        listings.at[i, 'url'] = clean_url(row['url'])
        listings.at[i, 'street_address'] = clean_street_address(row['street_address'])
        listings.at[i, 'price'] = clean_price(row['price'])
        listings.at[i, 'num_bedroom'] = clean_num_bedroom(row['num_bedroom'])
        listings.at[i, 'num_bathroom'] = clean_num_bathroom(row['num_bathroom'])
        listings.at[i, 'cost_psf'] = clean_cost_psf(row['cost_psf'])
        listings.at[i, 'total_area'] = clean_total_area(row['total_area'])
        listings.at[i, 'walk'] = clean_walk(row['walk'])
        listings.at[i, 'tags'] = clean_tags(row['tags'])
        listings.at[i, 'recency'] = clean_recency(row['recency'])


    listings['price'] = listings['price'].astype(float)
    listings['cost_psf'] = listings['cost_psf'].astype(float)

    if onemap_search_db!=None:
        with open(onemap_search_db, 'r') as f:
            search_db = json.load(f)

        listings['address'], \
        listings['road_name'], \
        listings['building'], \
        listings['postal_code'], \
        listings['latitude'], \
        listings['longitude'] = zip(*listings['street_address'].apply(lambda x: process_street_address(x, search_db)))


    search_phrases = listings[listings['street_address'].notna()]['street_address'].values.tolist()

    onemap_search_phrase_temp_file = './temp.json'
    with open(onemap_search_phrase_temp_file, 'w') as f:
        json.dump(search_phrases, f)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
    
    loop.run_until_complete(onemap_search_addresses(
        input_file=onemap_search_phrase_temp_file,
        output_file=onemap_search_db
    ))
    
    

    listings['address'], \
    listings['road_name'], \
    listings['building'], \
    listings['postal_code'], \
    listings['latitude'], \
    listings['longitude'] = zip(*listings['street_address'].apply(lambda x: process_street_address(x, search_db)))


    search_phrases = listings[listings['latitude'].isna()]['name'].values.tolist()
    with open(onemap_search_phrase_temp_file, 'w') as f:
        json.dump(search_phrases, f)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
    
    loop.run_until_complete(onemap_search_addresses(
        input_file=onemap_search_phrase_temp_file,
        output_file=onemap_search_db
    ))

    os.remove(onemap_search_phrase_temp_file)

    with open(onemap_search_db, 'r') as f:
        search_db = json.load(f)
        
    listings['address'], \
    listings['road_name'], \
    listings['building'], \
    listings['postal_code'], \
    listings['latitude'], \
    listings['longitude'] = zip(*listings['street_address'].apply(lambda x: process_street_address(x, search_db)))


    listings['floor_area'] = listings['total_area'].apply(lambda x: x['floor'])
    listings['land_area'] = listings['total_area'].apply(lambda x: x['land'])
    
    listings['walk_destination'] = listings['walk'].apply(lambda x: x['destination'])
    listings['walk_distance_m'] = listings['walk'].apply(lambda x: process_walk_distance(x['distance']))
    listings['walk_time_mins'] = listings['walk'].apply(lambda x: process_walk_time(x['time']))
    
    listings['lease_duration'], \
    listings['completion'], \
    listings['type'] = zip(*listings['tags'].apply(lambda x: process_tags(x)))

    listings = listings.drop(columns=['street_address', 'total_area', 'walk', 'tags', 'recency'])

    listings.to_csv(output_file, index=False)

    

def clean_name(name):
    if name is None:
        return None
    name = name.strip()
    return name

def clean_url(url):
    if url is None:
        return None
    return url

def clean_street_address(address):
    if address is None:
        return None
    address = address.strip()
    return address

def clean_price(price):
    if price is None:
        return None
    price = price.strip()
    price = re.search(r'[\d,]+(\.\d+)?',price)
    if price:
        price = float(price.group(0).replace(',','').strip())
    else:
        price = None
    return price

def clean_num_bedroom(num_bedroom):
    if num_bedroom is None:
        return None
    num_bedroom = int(num_bedroom.strip())
    return num_bedroom

def clean_num_bathroom(num_bathroom):
    if num_bathroom is None:
        return None
    num_bathroom = int(num_bathroom.strip())
    return num_bathroom

def clean_cost_psf(cost_psf):
    if cost_psf is None:
        return None
    cost_psf = cost_psf.strip()
    pattern = r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?"
    cost_psf = re.search(pattern, cost_psf)
    cost_psf = float(cost_psf.group(0).replace(',', ''))
    return cost_psf

def clean_total_area(total_area):
    if total_area is None:
        return None
    total_area = total_area.strip()
    if ',' in total_area:

        cleaned = {'floor': None, 'land': None}
        total_area = total_area.split(',')
        for area in total_area:
            keyword = re.search(r'\((.*?)\)', area).group(1).strip()
            size = int(re.search(r'(\d+)', area).group(0))

            cleaned[keyword] = size
    else:
        cleaned = {
            'floor': int(re.search(r'(\d+)', total_area).group(0)),
            'land': None
        }
    
    return cleaned

def clean_walk(walk):
    results = {'destination': None, 'distance': None, 'time': None}
    if walk is not None:
        walk = walk.strip()
        results['destination'] = re.search(r'to (.*)', walk).group(1).strip()
        results['distance'] = re.search(r'\((.*?)\)', walk).group(1).strip()
        results['time'] = re.search(r'(.*?)\s*\(', walk).group(1).strip()
    
    return results


def clean_tags(tags):
    if tags is None:
        return None
    for i in range(len(tags)):
        tags[i] = tags[i].strip()
    return tags


def clean_recency(recency):
    if recency is None:
        return None
    recency = recency.strip()
    return recency

def process_street_address(address, search_db):
    if address is None or address not in search_db:
        return None, None, None, None, None, None
    elif len(search_db[address])==1:
        x = search_db[address][0]
        add = x['ADDRESS'] if 'ADDRESS' in x and x['ADDRESS']!='NIL' else None
        road_name = x['ROAD_NAME'] if 'ROAD_NAME' in x and x['ROAD_NAME']!='NIL' else None
        building = x['BUILDING'] if 'BUILDING' in x and x['BUILDING']!='NIL' else None
        postal_code = x['POSTAL'] if 'BUILDING' in x and x['POSTAL']!='NIL' else None
        lat = x['LATITUDE'] if 'LATITUDE' in x and x['LATITUDE']!='NIL' else None
        long = x['LONGITUDE'] if 'LONGITUDE' in x and x['LONGITUDE']!='NIL' else None
        return add, road_name, building, postal_code, lat, long

    return None, None, None, None, None, None

def process_walk_distance(distance):
    if distance is None:
        return None
    num, unit = distance.split(' ')
    num = int(num)
    if unit.lower()=='km':
        num = num * 1000
    return num

def process_walk_time(time):
    if time is None:
        return None
    num, unit = time.split(' ')
    num = int(num)
    return num

def process_tags(tags):
    processed = {
        'lease_duration': None,
        'completion': None,
        'type': None
    }
    for tag in tags:
        string = tag.lower()
        if 'freehold' in string:
            processed['lease_duration'] = 'Freehold'
        elif 'unknown tenure' in string:
            pass
        elif 'leasehold' in string:
            processed['lease_duration'] = int(re.search(r'\d+', tag).group(0))
        elif 'built' in string or 'completion' in string:
            processed['completion'] = int(re.search(r'\d+', tag).group(0))
        else:
            processed['type'] = tag
    
    return processed['lease_duration'], processed['completion'], processed['type']

