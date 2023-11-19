import json
from math import radians, cos, sin, asin, sqrt

# accepts 'childcare','college', 'disability_service','eldercare','hawker','kindergarten','mall','npark','preschool','primary_school','secondary_school',
# 'sport_facility' as type parmeter in search_nearby_amenities function
valid_amenities = frozenset(['childcare','college', 'disability_service','eldercare','hawker','kindergarten','mall','npark','preschool','primary_school','secondary_school','sport_facility','cycling_path'])


def haversine(lon1, lat1, lon2, lat2):
   """
   Calculate the great circle distance in kilometers between two points 
   on the earth (specified in decimal degrees)
   """

   # convert decimal degrees to radians 
   lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
   # haversine formula 
   dlon = lon2 - lon1 
   dlat = lat2 - lat1 
   a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
   c = 2 * asin(sqrt(a)) 
   # Radius of earth in kilometers is 6371
   distance = 6371* c
   return distance


# default threshold for nearby amenity is set at 3km
def search_nearby_amenities(lat1,long1,type='childcare',threshold=3):
    """

    return format for all types of amenities except cycling_path
    [
        {
            'name': "SparkleTots",
            'lat': 1.31283861068763
            'long': 103.31283861068763
        },
        {
            'name': "SparkleTots 2",
            'lat': 1.21323861068763
            'long': 103.41683861068763
        },...
    ]

    return format for cycling_path (coordinates forms a line on the map)
    [
        {
            'name':'Toa Payoh',
            'latlng':[[1.31283861068763,103.31283861068763],[1.21323861068763,103.41683861068763]]
        }
    ]

"""
    if type not in valid_amenities:
        raise ValueError("results: type must be one of %r" % valid_amenities)
    
    nearby_results = []
    with open(f'./amenities/{type}_coords.json','r') as f:
        locations_coord = json.load(f)
    if type == 'cycling_path':
        for coord_list in locations_coord['results']:
            # check if any point along cycling path is within threshold distance
            for coord in coord_list['latlng']:
                lat2 = coord[0]
                long2 = coord[1]
                distance = haversine(long1,lat1,long2,lat2)
                if distance<threshold:
                    nearby_results.append(coord_list)
                    break

    else:
        for coord in locations_coord['results']:
            lat2 = coord['lat']
            long2 = coord['long']
            distance = haversine(long1,lat1,long2,lat2)
            # if distance is less than 3km we consider it as a nearby_result
            if distance<threshold:
                nearby_results.append(coord)    
    
    return nearby_results
