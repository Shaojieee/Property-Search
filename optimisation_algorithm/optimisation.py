import os
import sys
sys.path.append(os.path.join(os.getcwd(), os.pardir))

import pandas as pd
import numpy as np
from onemap_client import OneMapClient
import pyproj

import asyncio
import aiohttp
from dotenv import load_dotenv
load_dotenv()

email = os.environ['ONE_MAP_API_EMAIL']
password = os.environ['ONE_MAP_API_PASSWORD']

Client = OneMapClient(email, password)
token = Client.get_token(email, password)


def cost_fn(time, freq):
    # We should change this to scale accordingly
    return np.exp(time)*freq


def get_travelling_time(start, end, travel_mode, client):
    while True:
        if travel_mode=='pt':
            journey = client.get_public_transport_route(
                start, 
                end, 
                date='01-14-2023',
                time='13:00:00',
                mode='TRANSIT',
            )
            # TODO: Calculate distance

            if 'plan' in journey:
                return (journey['plan']['itineraries'][0]['walkTime'] + journey['plan']['itineraries'][0]['transitTime'])/60/60, 0
        else:
            journey = client.get_route(start, end, route_type=travel_mode)

            if 'route_summary' in journey:
                return journey['route_summary']['total_time']/60/60, journey['route_summary']['total_distance']

    


# Get weighted mid point. Weighted by travelling frequency
def get_mid_point(locations):
    coors = np.array([x['coor'] for x in locations])
    freq = np.array([x['freq'] for x in locations])
    midpoint = np.average(coors, axis=0, weights=freq)
    return midpoint


def objective_func(locations, cur):
    total_cost = 0
    individual_costs = {}
    for location in locations:
        coor = location['coor']
        freq = location['freq']
        travel_mode = location['travel_type']
        time, distance = get_travelling_time(coor, cur, travel_mode, Client)
        cost = cost_fn(time,freq)
        total_cost += cost
        individual_costs[tuple(coor)] = cost
        
    print(f'Total Cost: {total_cost}')
    return total_cost, individual_costs

# Return the resultant cost direction in degrees.
def get_direction(ind_costs, origin):
    locations = list(ind_costs.keys())
    costs = np.array([ind_costs[x] for x in locations]).reshape(len(locations),1)
    locations = np.array(locations)
    origin = np.array(origin)

    geodesic = pyproj.Geod(ellps='WGS84')
    bearings = []
    for location in locations:
        fwd_azimuth,back_azimuth,distance = geodesic.inv(origin[1], origin[0], location[1], location[0])
        bearings.append(fwd_azimuth)

    bearings = np.array(bearings).reshape(len(locations),1)
    # print(bearings)
    v_cost_vectors =  costs * np.cos(bearings*np.pi/180)
    # print(v_cost_vectors)
    h_cost_vectors = costs * np.sin(bearings*np.pi/180)
    # print(h_cost_vectors)
    cost_vectors = np.hstack([v_cost_vectors, h_cost_vectors])
    # print(cost_vectors)
    sum_cost_vectors = np.sum(cost_vectors, axis=0)
    print(f'Resultant Cost:{sum_cost_vectors}')

    resultant_bearing = np.arctan(abs(sum_cost_vectors[0] / sum_cost_vectors[1]))*180/np.pi

    if sum_cost_vectors[0]>=0:
        if sum_cost_vectors[1]>=0:
            return resultant_bearing
        else:
            return 360-resultant_bearing
    else:
        if sum_cost_vectors[1]>=0:
            return 90+resultant_bearing
        else:
            return 180+resultant_bearing
        

def update_point(cur, bearings, distance_to_move_km=2):
    geodesic = pyproj.Geod(ellps='WGS84')
    long, lat, back_azimuth = geodesic.fwd(cur[1], cur[0], bearings, distance_to_move_km*1000)
    return lat,long


def optimise(locations, iterations=10):
    point = get_mid_point(locations)
    coors = np.array([x['coor'] for x in locations])
    bounds = ((np.min(coors[:,0]), np.max(coors[:,0])), (np.min(coors[:,1]), np.max(coors[:,1])))

    results = {'coor': [], 'total_cost': [], 'ind_costs': []}
    early_stop_count = 0
    lowest_cost = float('inf')
    for iter in range(iterations):
        results['coor'].append(point)
        costs, ind_costs = objective_func(locations, point)
        results['total_cost'].append(costs); results['ind_costs'].append(ind_costs)

        if lowest_cost>costs:
            early_stop_count = 0
            lowest_cost = costs
        else:
            early_stop_count+=1
        # if early_stop_count==5:
        #     break

        update_bearings = get_direction(ind_costs, point)
        point = update_point(point, update_bearings)
        
    lowest_cost_idx = np.argmin(results['total_cost'])
    best_point = results['coor'][lowest_cost_idx]
    return best_point, results




def get_properties_distance(best_location, properties_file):
    properties = pd.read_csv(properties_file)

    properties = properties[(properties['latitude'].notna()) & (properties['longitude'].notna())]

    properties['distance'] = None 

    geodesic = pyproj.Geod(ellps='WGS84')
    for i, row in properties.iterrows():
        properties.at[i,'distance'] = geodesic.inv(best_location[1], best_location[0], row['longitude'], row['latitude'])[2]

    return properties


if __name__=='__main__':
    locations = [
        # Changi Airport
        {'coor': [1.334961708552094, 103.96292017145929], 'freq': 1, 'travel_type': 'drive'},
        # Murai Camp
        {'coor': [1.3869972483354562, 103.70085045003314], 'freq': 7, 'travel_type': 'drive'},
        # Clarke Quay
        {'coor': [1.2929040296020744, 103.84729261914465], 'freq': 7, 'travel_type': 'drive'}
    ]
    import time 
    start = time.time()
    optimise(locations)
    end = time.time()

    print(f'Time taken:{end-start}')