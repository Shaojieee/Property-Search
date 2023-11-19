import folium
import streamlit as st

import sys
sys.path.append('./')
from optimisation_algorithm import optimisation as op
from onemap_client import OneMapClient

def generate_map():
    m = folium.Map(
        location=(1.3674754117016408, 103.81093951150724), 
        zoom_start=11,
        min_zoom=11
    )
    # m.add_child(folium.ClickForMarker())
    return m

def optimise():
    best_location, results = op.optimise(st.session_state['locations'])  
    st.session_state['best_location'] = [best_location]

    # for location in st.session_state['locations']:
    st.session_state['properties'] = op.get_properties_distance(best_location, './property_guru/search/processed/20231116/processed.csv')

    top_5_properties = st.session_state['properties'].sort_values(by=['distance'], ascending=True).head(5)

    st.session_state['top_5_properties'] = top_5_properties


def add_to_journey(address, travel_type, frequency):
    st.session_state['locations'].append({'coor': address, 'freq': frequency, 'travel_type': travel_type})


def search_address(search):
    client = OneMapClient('', '')
    results = client.search(search)
    if results is None or 'error' in results:
        return []
    else:
        return results['results']