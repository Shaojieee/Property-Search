import streamlit as st
import folium
from streamlit_folium import st_folium
import polyline
from streamlit_option_menu import option_menu
import math

import sys
sys.path.append('./')
from streamlit_dashboard.utils import generate_map, get_route, get_amenities
from data.return_nearby_amenities import valid_amenities

def section_2():

    if 'selected_lat_lng' not in st.session_state:
        st.session_state['selected_lat_lng'] = {'lat': None, 'lng': None}

    if 'last_selected_lat_lng' not in st.session_state:
        st.session_state['last_selected_lat_lng'] = None

    st.header('Best Locations')

    filter_properties = st.session_state['properties']
    amenity_col, housing_col, price_col = st.columns(3)

    # Amenities Filter
    with amenity_col:
        st.multiselect(
            label='Amenities',
            options=valid_amenities,
            key='selected_amenities'
        )
        for amenity in st.session_state['selected_amenities']:
            filter_properties = filter_properties[filter_properties[f'has_{amenity}']==True]

    with housing_col:
        st.selectbox(
            label='Property Type',
            options=filter_properties['type'].unique(),
            index=None,
            key='selected_housing_type'
        )

        if st.session_state['selected_housing_type']!=None:
            filter_properties = filter_properties[filter_properties['type']==st.session_state['selected_housing_type']]

    
    # Price filter
    with price_col:
        filter_properties = filter_properties.loc[filter_properties['price']!='Price on ask', :]
        filter_properties.loc[:,'price'] = filter_properties.loc[:,'price'].astype(float)
        prices = filter_properties['price']

        min_price_col, max_price_col = st.columns(2)
        with min_price_col:
            st.number_input(
                'Minimum Price',
                value=float(prices.min()),
                min_value = float(prices.min()),
                max_value = float(prices.max()) if 'selected_price_max' not in st.session_state else st.session_state['selected_price_max'],
                key = 'selected_price_min',
                step=100000.00,
                format='%f'
            )
        with max_price_col:
            st.number_input(
                'Maximum Price',
                value=float(prices.max()),
                min_value = float(prices.min()) if 'selected_price_min' not in st.session_state else st.session_state['selected_price_min'],
                max_value = float(prices.max()),
                key = 'selected_price_max',
                step=100000.00,
                format='%f'
            )

        filter_properties = filter_properties[(filter_properties['price']>=st.session_state['selected_price_min']) & (filter_properties['price']<=st.session_state['selected_price_max'])]
        

    to_display_lat_lng = filter_properties.groupby(by=['latitude', 'longitude'])['distance_km'].max().reset_index()
    to_display_lat_lng = to_display_lat_lng.sort_values(by=['distance_km'], ascending=True).head(5)

    filter_properties = filter_properties[filter_properties[['latitude', 'longitude']].apply(list, axis=1).isin(to_display_lat_lng[['latitude', 'longitude']].values.tolist())]

    if st.session_state['selected_lat_lng']!=None:
        amenities = get_amenities(
            latitude=st.session_state['selected_lat_lng']['lat'],
            longitude=st.session_state['selected_lat_lng']['lng'],
            amenity_types=st.session_state['selected_amenities'])

    map = generate_map()
    fg = folium.FeatureGroup(name="fg")
    
    for best in st.session_state['best_location']:
        fg.add_child(
            folium.Marker(
                location=best,
                popup='Ideal Location',
                tooltip='Ideal Location',
                icon=folium.Icon(color='red')
            )
        )
    for location in st.session_state['locations']:
        fg.add_child(
            folium.Marker(
                location=location['coor'],
                tooltip=location['name'],
                icon=folium.Icon(color='blue')
            )
        )

    if st.session_state['selected_lat_lng']!=None:
        for amenity in st.session_state['selected_amenities']:
            nearby_amenities = amenities[(amenities['amenity_type']==amenity)]
            for i,row in nearby_amenities.iterrows():
                fg.add_child(
                    folium.Marker(
                        location=(row['amenity_latitude'], row['amenity_longitude']),
                        tooltip=f"""{amenity}: {row['amenity_name']}""",
                        icon=folium.Icon(color='orange')
                    )
                )

    
    for i, row in to_display_lat_lng.iterrows():
        selected = row['latitude']==st.session_state['selected_lat_lng']['lat'] and row['longitude']==st.session_state['selected_lat_lng']['lng']
        fg.add_child(
            folium.Marker(
                location=(row['latitude'], row['longitude']),
                tooltip='Click to view more information',
                icon=folium.Icon(color='green') if selected else folium.Icon(color='lightgray')
            )
        )

        if selected:
            for location in st.session_state['locations']:
                route_details = get_route(row['latitude'], row['longitude'], location['coor'][0], location['coor'][1], location['travel_type'])
                # print(route_details)
                if route_details is not None:
                    route = polyline.decode(route_details['route_geometry'])

                    fg.add_child(
                        folium.PolyLine(
                            locations=route,
                            weight=4,
                            tooltip=f"Time: {int(route_details['total_time']/60)} mins"
                        )
                    )

        

    st_data = st_folium(
        map, 
        feature_group_to_add=fg,
        use_container_width=True,
        key='property_map'
    )

    if (st_data["last_object_clicked"] and st_data["last_object_clicked"] != st.session_state["last_selected_lat_lng"]):
        object_click_lat = st_data['last_object_clicked']['lat']
        object_click_long = st_data['last_object_clicked']['lng']

        if [object_click_lat, object_click_long] in to_display_lat_lng[['latitude', 'longitude']].values.tolist():
            st.session_state["last_selected_lat_lng"] = st_data["last_object_clicked"]
            st.session_state["selected_lat_lng"] = st_data["last_object_clicked"]
            st.rerun()


    to_print_details = filter_properties[(filter_properties['latitude']==st.session_state['selected_lat_lng']['lat']) & (filter_properties['longitude']==st.session_state['selected_lat_lng']['lng'])]
    st.header('Listings Available')
    if len(to_print_details)==0:
        st.markdown('#### Select a grey marker on the map to view listings!')
    if len(to_print_details)>0:
        st.markdown('#### Below are the available listings on Property Guru at the green marker!')
        selection_col, detail_col = st.columns((1,3))
        
        names = []
        for i, row in to_print_details.iterrows():
            names.append(row['name']+' - '+str(row['id']))
        
        with selection_col:
            property_detail_selected = option_menu(
                '',
                names,
                default_index=0,
                icons=['house']*len(names),
                styles={
                    'container': {'height':'500px', 'overflow-y':'auto'}
                }
            )
        
        with detail_col:
            st.write()
            property_name_selected, property_id_selected = property_detail_selected.split(' - ')
            details = to_print_details.loc[to_print_details['id']==int(property_id_selected)].iloc[0]
            st.header(details['name'])
            st.subheader('URL')
            st.write(details['url'])

            
            st.subheader('Address')
            st.write(details['address'])
            price_col, area_col, room_col = st.columns(3)
            with price_col:
                st.subheader('Price')
                st.write('$'+f"{details['price']:,.2f}" if not math.isnan(details['price']) else 'Not Available')
                st.subheader('Cost psf')
                st.write('$'+ f"{details['cost_psf']:,.2f}" if not math.isnan(details['cost_psf']) else 'Not Available')
            with area_col:
                st.subheader('Floor Area')
                st.write(f"{int(details['floor_area']):,d}" if not math.isnan(details['floor_area']) else 'Not Available')
                st.subheader('Land Area')
                st.write(f"{int(details['land_area']):,d}" if not math.isnan(details['land_area']) else 'Not Available')
            with room_col:
                st.subheader('\# of bedrooms')
                st.write(str(int(details['num_bedroom'])) if not math.isnan(details['num_bedroom']) else 'Not Available')
                st.subheader('\# of bathrooms')
                st.write(str(int(details['num_bathroom'])) if not math.isnan(details['num_bathroom']) else 'Not Available')
