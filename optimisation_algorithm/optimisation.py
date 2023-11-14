import os
import sys
sys.path.append(os.path.join(os.getcwd(), os.pardir))

import pandas as pd
import numpy as np
import getpass
from onemap_client import OneMapClient
from scipy.optimize import minimize



# TODO: Create method to take into account of travelling frequency
# TODO: Create method that uses geometric distance
def initialise_starting_point(locations, method='middle'):
    # Ge the middle of all locations
    if method=='middle':
        return np.mean(locations, axis=0)
    
    return 


# TODO: Create a bound method that uses distance or travelling time
def get_bounds(locations, method='box'):
    # Creates rectangular search space.
    if method=='box':
        return ((np.min(locations[:,0]), np.max(locations[:,0])), (np.min(locations[:,1]), np.max(locations[:,1])))
    
    return


def get_travelling_time(start, end, onemap):
    journey = onemap.get_route(start, end, route_type='drive')

    # Convert minutes to hours
    return journey['route_summary']['total_time']/60, journey['route_summary']['total_distance']


def convert_journey_to_cost(time):
    # TODO: We should change this to scale appropriately
    return np.exp(time)


# TODO: Take account of travelling frequency
def objective_func(locations, cur, onemap):
    total_cost = 0
    for location in locations:
        time, distance = get_travelling_time(location, cur, onemap)
        total_cost += convert_journey_to_cost(time)
    return total_cost


def optimise(locations, bounds=None):
    starting_point = initialise_starting_point(locations)


    # TODO: Add constraints/bounds to include only valid Longitude and Latitude
    return minimize(
        fun=lambda x: objective_func(locations, x),
        x0=starting_point, 
        method='SLSQP', 
        bounds=bounds
    )