import folium
import streamlit as st
import polyline
import psycopg2

import os
import sys
sys.path.append('./')
from optimisation_algorithm import optimisation as op
from onemap_client import OneMapClient

from dotenv import load_dotenv
load_dotenv()


def generate_map():
    m = folium.Map(
        location=(1.3674754117016408, 103.81093951150724), 
        zoom_start=11,
        min_zoom=11
    )
    # m.add_child(folium.ClickForMarker())
    return m


def log_optimisation_run():

    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
        database=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )

    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO public.logs
        (id, run_time)
        VALUES(DEFAULT, CURRENT_TIMESTAMP) RETURNING id;
    """)

    id = cursor.fetchone()[0]

    for row in st.session_state['locations']:
        cursor.execute(f"""
            INSERT INTO locations 
            (runs_id, lat, long, travel_type, frequency)
            VALUES
            ({id}, {row['coor'][0]}, {row['coor'][1]}, '{row['travel_type']}', {row['freq']});
        """)

def optimise():

    st.session_state['locations'] = st.session_state['search_locations']

    best_location, results = op.optimise(st.session_state['locations'])  
    st.session_state['best_location'] = [best_location]
    
    st.session_state['properties'] = op.get_properties_distance(best_location, './final.csv')

    st.session_state['properties'] = st.session_state['properties'][st.session_state['properties']['distance']<5000]

    st.session_state['properties'] = st.session_state['properties'].sort_values(by=['distance'], ascending=True)

    log_optimisation_run()



def add_to_frequently_visited(name, address, travel_type_str, frequency):
    if name=='':
        name = f'Location {len(st.session_state["search_locations"])+1}'
    if travel_type_str=='Drive':
        travel_type='drive'
    elif travel_type_str=='Public Transport':
        travel_type='pt'
    elif travel_type_str=='Walk':
        travel_type='walk'
    st.session_state['search_locations'].append({'selected': False, 'name': name, 'coor': address, 'freq': frequency, 'travel_type': travel_type, 'travel_type_str':travel_type_str})


def search_address(search):
    client = OneMapClient('', '')
    results = client.search(search)
    if results is None or 'error' in results:
        return []
    else:
        return results['results']


def get_route(
        lat1, long1,
        lat2, long2,
        travel_type
):  
    input_key = tuple([lat1, long1, lat2, long2, travel_type])
    if 'property_route' not in st.session_state:
        st.session_state['property_route'] = {}
    
    if input_key in st.session_state['property_route']:
        return st.session_state['property_route'][input_key]
    
    email = os.environ['ONE_MAP_API_EMAIL']
    password = os.environ['ONE_MAP_API_PASSWORD']

    client = OneMapClient(email, password)
    client.get_token()
    if travel_type=='drive' or travel_type=='walk':
    
        resp = client.get_route(
            start_coordinates=(lat1, long1),
            end_coordinates=(lat2, long2),
            route_type=travel_type
        )

        resp['total_time'] = resp['route_summary']['total_time']
        resp['total_distance'] = resp['route_summary']['total_distance']

        st.session_state['property_route'][input_key] = resp

        return resp
    elif travel_type=='pt':
        resp = client.get_public_transport_route(
            (lat1, long1), 
            (lat2, long2), 
            date='01-14-2023',
            time='13:00:00',
            mode='TRANSIT',
        )

        resp = resp['plan']['itineraries'][0]
        resp['total_time'] = resp['walkTime'] + resp['transitTime']

        all_points = []
        for leg in resp['legs']:
            geometry = leg['legGeometry']['points']
            points = polyline.decode(geometry)

            all_points += points

        resp['route_geometry'] = polyline.encode(all_points)
        if resp!=None:
            st.session_state['property_route'][input_key] = resp

        return resp
    
