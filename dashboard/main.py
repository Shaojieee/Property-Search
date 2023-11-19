import streamsync as ss
import folium

# This is a placeholder to get you started or refresh your memory.
# Delete it or adapt it as necessary.
# Documentation is available at https://streamsync.cloud

# Shows in the log when the app starts
print("Hello world!")

# Its name starts with _, so this function won't be exposed
def _update_message(state, map):
    is_even = state["counter"] % 2 == 0
    message = ("+Even" if is_even else "-Odd")
    state["message"] = message
    state['map_html'] = map._repr_html_()
    state['map'] = map

def decrement(state):
    state["counter"] -= 1
    _update_message(state)

def increment(state):
    state["counter"] += 1
    # Shows in the log when the event handler is run
    print(f"The counter has been incremented.")
    _update_message(state)
    
# Initialise the state

# "_my_private_element" won't be serialised or sent to the frontend,
# because it starts with an underscore

def generate_map():
    m = folium.Map(location=(45.5236, -122.6750))
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

def place_marker_2(state):
    map = state['map']
    folium.Marker(
        location=[45.6000, -122.6750],
        tooltip="Click me!",
        popup="Mt. Hood Meadows",
        icon=folium.Icon(icon="cloud"),
    ).add_to(map)
    state['map_html'] = map._repr_html_()
    state['map'] = map
    print('Clicked')



initial_state = ss.init_state({
    "my_app": {
        "title": "My App"
    },
    "_my_private_element": 1337,
    "message": None,
    "counter": 26
})
_update_message(initial_state, generate_map())