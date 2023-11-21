import streamlit as st
import folium
from streamlit_folium import st_folium

import sys
sys.path.append('./')
from streamlit_dashboard.utils import generate_map, optimise, add_to_frequently_visited, search_address

def section_1():

    if 'search_locations' not in st.session_state:
        st.session_state['search_locations'] = []

    if 'last_search_clicked' not in st.session_state:
        st.session_state['last_search_clicked'] = None

    if 'search_results' not in st.session_state:
        st.session_state['search_results'] = None

    if 'selected_frequency' not in st.session_state:
        if 'previous_frequency' in st.session_state:
            st.session_state['selected_frequency'] = st.session_state['previous_frequency']
        else:
            st.session_state['selected_frequency'] = 1
        
    if 'search_address' not in st.session_state:
        st.session_state['search_address'] = ''


    col1, col2 = st.columns((3, 2))

    with col1:
        st.text_input(
            'Search Address',
            key='search_address'
        )

        if st.session_state['search_address']!='':
            search_results = search_address(st.session_state['search_address'])
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
            use_container_width=True,
            # height=330,
            key='search_map'
        )

        if search_map['last_clicked']!=None and search_map['last_clicked']!=st.session_state['last_search_clicked']:
            st.session_state['last_search_clicked'] = search_map['last_clicked']
            st.rerun()




    with col2:
        lat_col, lon_col = st.columns(2)
        with lat_col:
            st.text_input(
                'Latitude', 
                value = 'Select Location from Map' if st.session_state['last_search_clicked']== None else st.session_state['last_search_clicked']['lat'],
                disabled=True
            )
        with lon_col:
            st.text_input(
                'Longitude', 
                value = 'Select Location from Map' if st.session_state['last_search_clicked']== None else st.session_state['last_search_clicked']['lng'],
                disabled=True
            )
        
        st.text_input(
            'Name (Optional)',
            key='place_name'
        )


        st.radio(
            'Mode of Transport', 
            ['Drive', 'Public Transport', 'Walk'], 
            horizontal=True,
            key='travel_type'
        )

        def update_slider_value():
            st.session_state['previous_frequency'] = st.session_state['selected_frequency']

        st.slider(
            'Frequency per week', 
            1, 7,
            key='selected_frequency',
            on_change=update_slider_value
        )

        confirm = st.button(
            'Add to Frequently Visited Places',
            disabled=(st.session_state['last_search_clicked']==None),
            on_click=lambda:add_to_frequently_visited(
                st.session_state['place_name'],
                [float(st.session_state['last_search_clicked']['lat']),float(st.session_state['last_search_clicked']['lng'])], 
                st.session_state['travel_type'], 
                st.session_state['selected_frequency']
            ),
            use_container_width=True
        )

        st.subheader('Frequently Visited Places')

        data = st.data_editor(
            st.session_state['search_locations'],
            use_container_width=True,
            column_order=['selected', 'name', 'freq', 'travel_type_str'],
            column_config={
                'selected': st.column_config.CheckboxColumn(
                    label='',
                    default=False,
                    disabled=False
                ),
                'name': st.column_config.Column(
                    label="Name",
                    disabled=True
                ),
                'freq': st.column_config.Column(
                    label="Frequency",
                    disabled=True
                ),
                'travel_type_str': st.column_config.Column(
                    label="Mode of Transport",
                    disabled=True
                ),
            }
        )

        if st.button(label='Delete Selected Place', use_container_width=True, disabled=len(st.session_state['search_locations'])==0):
            new_data = [x for x in data if x['selected']==False]
            st.session_state['search_locations'] = new_data
            st.rerun()


        st.button(
            'Find Ideal Location',
            use_container_width=True,
            key='optimise_button',
            disabled=len(st.session_state['search_locations'])==0
        )

        if st.session_state['optimise_button']:
            optimise()
            
            