import streamsync as ss
import folium

# This is a placeholder to get you started or refresh your memory.
# Delete it or adapt it as necessary.
# Documentation is available at https://streamsync.cloud


# Its name starts with _, so this function won't be exposed
def _update_message(state, map):
    state['map_html'] = map._repr_html_()
    state['map'] = map

    
# Initialise the state

# "_my_private_element" won't be serialised or sent to the frontend,
# because it starts with an underscore

def generate_map():

    m = folium.Map(
        location=(1.3674754117016408, 103.81093951150724), 
        zoom_start=11,
        min_zoom=11,
    )
    m.add_child(folium.ClickForMarker())
    return m

def place_marker_1(state):
    map = state['map']
    
    folium.Marker(
        location=[45.5236, -122.6750],
        tooltip="Click me!",
        popup="Mt. Hood Meadows",
        icon=folium.Icon(icon="cloud"),
    ).add_to(map)
    state['map_html'] = map._repr_html_()
    state['map'] = map
    print('Clicked')

def get_marker_coor(state, payload):
    print('Clicked')


initial_state = ss.init_state({
    "initial_point": [1.3674754117016408, 103.81093951150724]
})

_update_message(initial_state, generate_map())