import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_card import card
from streamlit_extras.row import row
from st_keyup import st_keyup
import pandas as pd

import sys
sys.path.append('./')
from streamlit_dashboard.utils import generate_map, optimise, add_to_journey, search_address
from return_nearby_amenities import valid_amenities


st.set_page_config(layout='wide')

if 'locations' not in st.session_state:
    st.session_state['locations'] = [
    # # Changi Airport
    # {'coor': [1.334961708552094, 103.96292017145929], 'freq': 1},
    # # Murai Camp
    # {'coor': [1.3869972483354562, 103.70085045003314], 'freq': 7},
    # # Clarke Quay
    # {'coor': [1.2929040296020744, 103.84729261914465], 'freq': 7}
]

if 'best_location' not in st.session_state:
    st.session_state['best_location'] = []

if 'selected_property' not in st.session_state:
    st.session_state['selected_property'] = -1

if 'last_property_selected' not in st.session_state:
    st.session_state['last_property_selected'] = None

if 'last_search_clicked' not in st.session_state:
    st.session_state['last_search_clicked'] = None
    st.session_state['reset_search_clicked'] = None

if 'search_results' not in st.session_state:
    st.session_state['search_results'] = None


col1, col2 = st.columns((3, 2))

with col1:
    search = st.text_input(
        'Search Address'
    )
    if search!='':
        search_results = search_address(search)
        st.session_state['search_results'] = search_results
    else:
        st.session_state['search_results'] = None

    map = generate_map()
    
    search_fg = folium.FeatureGroup(
        name='search'
    )

    if st.session_state['search_results']!=None:
        for result in st.session_state['search_results']:
            search_fg.add_child(
                folium.Marker(
                    location = (result['LATITUDE'], result['LONGITUDE']),
                    tooltip=result['SEARCHVAL'],
                    icon=folium.Icon(color='blue')
                )
            )
    if st.session_state['last_search_clicked']!=None:
        search_fg.add_child(
            folium.Marker(
                location = (st.session_state['last_search_clicked']['lat'], st.session_state['last_search_clicked']['lng']),
                icon=folium.Icon(color='red')
            )
        )

    search_map = st_folium(
        map,
        feature_group_to_add=search_fg,
        use_container_width=True
    )



    if search_map['last_clicked']!=None and search_map['last_clicked']!=st.session_state['last_search_clicked'] and st.session_state['reset_search_clicked']!=search_map['last_clicked']:
        st.session_state['last_search_clicked'] = search_map['last_clicked']
        st.session_state['reset_search_clicked'] = None
        st.rerun()
    
    if st.button('Reset Map', use_container_width=True):
        st.session_state['reset_search_clicked'] = st.session_state['last_search_clicked']
        st.session_state['last_search_clicked'] = None
        st.rerun()



with col2:
    lat_col, lon_col = st.columns(2)
    with lat_col:
        st.text_input(
            'Latitude', 
            value = 'Select Destination from Map' if st.session_state['last_search_clicked']== None else st.session_state['last_search_clicked']['lat'],
            disabled=True
        )
    with lon_col:
        st.text_input(
            'Longitude', 
            value = 'Select Destination from Map' if st.session_state['last_search_clicked']== None else st.session_state['last_search_clicked']['lng'],
            disabled=True
        )
       
    travel_type = st.radio('Travel Methods', ['Drive', 'Public Transport', 'Walk'], horizontal=True)
    frequency = st.slider('Frequency per week', 1, 7)

    confirm = st.button(
        'Add to Journey',
        disabled=(st.session_state['last_search_clicked']==None),
        on_click=lambda:add_to_journey([float(st.session_state['last_search_clicked']['lat']),float(st.session_state['last_search_clicked']['lng'])], travel_type, frequency),
        use_container_width=True
    )

    st.subheader('Frequently visited places')

    data = st.data_editor(
        st.session_state['locations'],
        num_rows='dynamic',
        use_container_width=True,
    )

    st.session_state['locations'] = data

    optimise = st.button(
        'Find Ideal Location',
        on_click=optimise,
        use_container_width=True,
)




map = generate_map()
fg = folium.FeatureGroup(name="fg")
map.add_child(fg)
for best in st.session_state['best_location']:
    fg.add_child(
        folium.Marker(
            location=best,
            popup='Ideal Location',
            tooltip='Ideal',
            icon=folium.Icon(color='red')
        )
    )
for location in st.session_state['locations']:
    fg.add_child(
        folium.Marker(
            location=location['coor'],
            popup='Search',
            tooltip='Search',
            icon=folium.Icon(color='blue')
        )
    )
if 'top_5_properties' in st.session_state:
    for i, row in st.session_state['top_5_properties'].iterrows():
        fg.add_child(
            folium.Marker(
                location=(row['latitude'], row['longitude']),
                tooltip='Click to view more information',
                popup=row['id'],
                icon=folium.Icon(color='green') if row['id']==st.session_state['selected_property'] else folium.Icon(color='lightgray')
            )
        )

col1, col2 = st.columns((1, 5))
with col2:
    st_data = st_folium(
        map, 
        feature_group_to_add=fg,
        use_container_width=True,
        height=1000
    )

with col1:
    st.subheader('Nearby Amenities')

    for i in valid_amenities:
        st.checkbox(i)


if (
    st_data["last_object_clicked_popup"]
    and st_data["last_object_clicked_popup"] != st.session_state["last_property_selected"]
):
    st.session_state["last_property_selected"] = st_data["last_object_clicked_popup"]
    state = st_data["last_object_clicked_popup"]
    st.session_state["selected_property"] = int(state)
    st.rerun()



if 'top_5_properties' in st.session_state and st.session_state['selected_property'] in st.session_state['top_5_properties']['id'].values:
    st.subheader('Selected Property')
    df = st.session_state['top_5_properties']
    row = df[df['id']==st.session_state['selected_property']].iloc[0,:]

    st.subheader('URL')
    st.write(row['url'])
    st.subheader('Address')
    st.write(row['address'])
    st.subheader('Price')
    st.write('$'+str(row['price']))
    st.subheader('Cost psf')
    st.write('$'+str(row['cost_psf']))
    st.subheader('Floor Area')
    st.write(str(int(row['floor_area'])))
    st.subheader('\# of bedrooms')
    st.write(str(int(row['num_bedroom'])))
    st.subheader('\# of bathrooms')
    st.write(str(int(row['num_bathroom'])))


