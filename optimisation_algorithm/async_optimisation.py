import os
import sys
sys.path.append(os.path.join(os.getcwd(), os.pardir))

import pandas as pd
import numpy as np
from onemap_client import OneMapClient
import pyproj
import json
import ast
import html
import asyncio
import aiohttp
from dotenv import load_dotenv
load_dotenv()

email = os.environ['ONE_MAP_API_EMAIL']
password = os.environ['ONE_MAP_API_PASSWORD']

Client = OneMapClient(email, password)
token = Client.get_token(email, password)

def get_mid_point(locations):
    coors = np.array([x['coor'] for x in locations])
    freq = np.array([x['freq'] for x in locations])
    midpoint = np.average(coors, axis=0, weights=freq)
    return midpoint

 
def get_grid_points(mid_point, num_points):
    if num_points==1:
        return np.array([mid_point])
    
    bearings = np.arange(0, 360, 360/num_points)

    geodesic = pyproj.Geod(ellps='WGS84')

    longs, lats, fwd_az = geodesic.fwd(lons=[mid_point[1]]*num_points, lats=[mid_point[0]]*num_points, az=bearings, dist=[5*1000]*num_points)

    longs.append(mid_point[1])
    lats.append(mid_point[0])
    grid_points = np.vstack((lats,longs)).transpose()

    return grid_points

async def async_get_travelling_time(start, end, travel_type, session):
    while True:
        if travel_type=='pt':
            journey = await Client.async_get_public_transport_route(
                start, 
                end, 
                date='01-14-2023',
                time='13:00:00',
                mode='TRANSIT',
                session=session
            )

            if journey!=None and'plan' in journey:
                time = (journey['plan']['itineraries'][0]['walkTime'] + journey['plan']['itineraries'][0]['transitTime'])/60/60
                return [time]
        else:
            journey = await Client.async_get_route(start, end, route_type=travel_type, session=session)

            if journey!=None and 'route_summary' in journey:
                time = journey['route_summary']['total_time']/60/60
                return [time]
            elif journey!=None and 'API limit(s) exceeded' in journey['message']:
                print('API Limit Exceed')
                await asyncio.sleep(5)
            elif journey!=None and journey['status']=='error':
                try:
                    error_json = json.loads(html.unescape(journey['message']))
                    if 'Unable to get drive route' in error_json['error']:
                        return [-1]
                except:
                    print(journey)
                

def cost_fn(time, freq):
    return np.exp(time*freq)

# In degrees
def get_direction(travel_locations, search_locations):

    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth,back_azimuth,distance = geodesic.inv(
        lats1=search_locations[:,0], 
        lons1=search_locations[:,1], 
        lats2=travel_locations[:,0], 
        lons2=travel_locations[:,1]
    )
    
    return fwd_azimuth.reshape(len(search_locations),1)

def resolve_cost_vectors(azimuth, costs):
    v_cost_vectors =  costs * np.cos(azimuth*np.pi/180)
    h_cost_vectors = costs * np.sin(azimuth*np.pi/180)
    cost_vectors = np.hstack([v_cost_vectors, h_cost_vectors])

    return cost_vectors

def update_points(search_locations, azimuth, step=1*1000):
    geodesic = pyproj.Geod(ellps='WGS84')
    lons, lats, back_azimuth = geodesic.fwd(
        lats=search_locations[:,0],
        lons=search_locations[:,1],
        az=azimuth[:,0],
        dist=[step]*len(search_locations)
    )

    return np.vstack((lats,lons)).transpose()


async def async_optimise_step(locations, search_locations):
    num_search_location = len(search_locations)
    num_locations = len(locations)

    travel_locations = np.array([[x['coor'][0], x['coor'][1]] for x in locations])
    travel_frequency = np.array([[x['freq']]for x in locations])
    travel_type = np.array([[x['travel_type']]for x in locations])

    travel_locations = np.tile(travel_locations, (num_search_location,1))
    travel_frequency = np.tile(travel_frequency, (num_search_location,1))
    travel_type = np.tile(travel_type, (num_search_location,1))

    expand_search_array = np.repeat(search_locations, num_locations, axis=0)


    async with aiohttp.ClientSession() as session:
        tasks = []
        print(f'No. of api calls: {len(expand_search_array)}')
        for i in range(len(expand_search_array)):
                tasks.append(
                    async_get_travelling_time(
                        start=expand_search_array[i],
                        end=travel_locations[i],
                        travel_type=travel_type[i][0],
                        session=session
                    )
                )
        responses = await asyncio.gather(*tasks)
    
    travel_time = np.array(responses)

    # Removing invalid coor
    mask = travel_time!=[-1]
    mask = np.all(mask, axis=1)
    if ~np.any(mask):
        return [], None, None
    travel_frequency = travel_frequency[mask]
    travel_locations = travel_locations[mask]
    travel_type = travel_type[mask]
    travel_time = travel_time[mask]
    expand_search_array = expand_search_array[mask]
    search_locations = np.unique(expand_search_array, axis=0)

    costs = cost_fn(travel_time, travel_frequency)
    
    fwd_azimuth = get_direction(travel_locations, expand_search_array)
    
    # vertical_cost, horizontal_cost
    cost_vectors = resolve_cost_vectors(fwd_azimuth, costs)
    
    resultant_cost_vectors = np.array([np.sum(cost_vectors[np.all(expand_search_array==val, axis=1)],axis=0) for val in search_locations])
    print(resultant_cost_vectors)
    resultant_azimuth = np.degrees(np.arctan2(resultant_cost_vectors[:,1], resultant_cost_vectors[:,0])).reshape(-1,1)
    print(resultant_azimuth)
    updated_search_location = update_points(search_locations, resultant_azimuth)

    total_costs = np.power(resultant_cost_vectors, 2)
    total_costs = np.sum(total_costs,axis=1)
    total_costs = np.sqrt(total_costs)

    total_time = travel_time * travel_frequency
    total_time = np.array([np.sum(total_time[np.all(expand_search_array==val, axis=1)],axis=0) for val in search_locations])
    print(total_time)

    return updated_search_location, total_costs, total_time


def async_optimise(locations, iterations=10, num_points=1):
    weighted_mid_point = get_mid_point(locations)
    search_locations = get_grid_points(weighted_mid_point, num_points=num_points)

    results = {'coor': [], 'total_cost': [], 'total_time': []}
    for iter in range(iterations):
        
        loop = asyncio.get_event_loop()
        search_locations, total_costs, total_time = loop.run_until_complete(async_optimise_step(locations, search_locations))
        if len(search_locations)==0:
            break

        results['coor']+=search_locations.tolist()
        results['total_cost']+=total_costs.tolist()
        results['total_time']+=total_time.tolist()
    
    print(results)

        


if __name__=='__main__':
    locations = [
        # Changi Airport
        {'coor': [1.334961708552094, 103.96292017145929], 'freq': 7, 'travel_type': 'drive'},
        # Murai Camp
        {'coor': [1.3869972483354562, 103.70085045003314], 'freq': 7, 'travel_type': 'drive'},
        # Clarke Quay
        {'coor': [1.2929040296020744, 103.84729261914465], 'freq': 1, 'travel_type': 'drive'}
    ]
    import time 
    start = time.time()
    async_optimise(locations, iterations=10, num_points=4)
    end = time.time()

    print(f'Time taken:{end-start}')



        
        



    

        