import folium
import streamlit as st
import polyline
import psycopg2
import pandas as pd

import os
import sys
sys.path.append('./')
from optimisation_algorithm import optimisation as op
from optimisation_algorithm import async_optimisation as async_op
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


def optimise(run_async=True):

    st.session_state['locations'] = st.session_state['search_locations']
    if run_async:
        best_location, results = async_op.async_optimise(st.session_state['locations'], iterations=5, num_points=4)
    else:
        best_location, results = op.optimise(st.session_state['locations'])  
    st.session_state['best_location'] = [best_location]
    
    st.session_state['properties'] = get_properties(best_location, num_properties=1000)

    st.session_state['properties'] = st.session_state['properties'].sort_values(by=['distance_km'], ascending=True)

    log_optimisation_run()


def log_optimisation_run():
    try:
        conn = psycopg2.connect(
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT'],
            database=os.environ['OLTP_DB'],
            user=os.environ['OLTP_USER'],
            password=os.environ['OLTP_PASSWORD']
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
                (runs_id, name, lat, long, travel_type, frequency)
                VALUES
                ({id}, '{row['name']}', {row['coor'][0]}, {row['coor'][1]}, '{row['travel_type']}', {row['freq']});
            """)
    except psycopg2.OperationalError as ex:
        if 'Connection refused' not in str(ex):
            print(ex)


def get_route(
        lat1, long1,
        lat2, long2,
        travel_type
):  
    while True:
        try:
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
        except:
            print('Retrying')


def get_properties(best_location, num_properties=1000):
    try:
        conn = psycopg2.connect(
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT'],
            database=os.environ['OLAP_DB'],
            user=os.environ['OLAP_USER'],
            password=os.environ['OLAP_PASSWORD']
        )

        conn.autocommit = True
        cursor = conn.cursor()
        query = f"""
        SELECT 
            *,
            calculate_distance(latitude, longitude, {best_location[0]}, {best_location[1]}) as distance_km
        FROM
            public.properties
        ORDER BY 
            distance_km asc
        LIMIT {num_properties}
        """

        df = pd.read_sql_query(query, conn)
        return df
    
    except psycopg2.OperationalError as ex:
        if 'Connection refused' not in str(ex):
            print(ex)


def get_amenities(property_ids, amenity_types, num_amenities=5):
    
    try:
        conn = psycopg2.connect(
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT'],
            database=os.environ['OLAP_DB'],
            user=os.environ['OLAP_USER'],
            password=os.environ['OLAP_PASSWORD']
        )

        conn.autocommit = True
        cursor = conn.cursor()
        amenity_types_str = "'" + "','".join(amenity_types) + "'"
        property_ids_str = ','.join(property_ids.astype(str))
        query = f"""
        SELECT 
            *
        FROM 
        (
            SELECT 
                *,
                RANK() OVER (PARTITION BY amenity_type, property_id ORDER BY distance_km ASC) AS ranking
            FROM
                public.property_amenities 
            where 
                amenity_type IN ({amenity_types_str})
            AND
                property_id IN ({property_ids_str})
        )
        WHERE 
            ranking<={num_amenities}
        """

        df = pd.read_sql_query(query, conn)
        return df

    except psycopg2.OperationalError as ex:
        if 'Connection refused' not in str(ex):
            print(ex)
