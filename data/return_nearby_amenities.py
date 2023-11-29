import json
from math import radians, cos, sin, asin, sqrt
import pyproj
import numpy as np

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
    existing_lat_longs = set()
    with open(f'./amenities/{type}_coords.json','r') as f:
        locations_coord = json.load(f)
    if type == 'cycling_path':
        for coord_list in locations_coord['results']:
            # check if any point along cycling path is within threshold distance
            lats_lons = np.array(coord_list['latlng'])
            lons2 = lats_lons[:,1]
            lats2 = lats_lons[:,0]

            lons1 = np.array([long1] * len(lons2))
            lats1 = np.array([lat1] * len(lats2))

            geodesic = pyproj.Geod(ellps='WGS84')
            fwd_azimuth, back_azimuth, distance_m = geodesic.inv(
                lons1=lons1,
                lats1=lats1,
                lons2=lons2,
                lats2=lats2,
            )
            
            min_idx = np.argmin(distance_m)
            if distance_m[min_idx]<=threshold*1000:
                coord_list['distance_km'] = distance_m[min_idx]/1000.0
                coord_list['lat'] = lats2[min_idx]
                coord_list['long'] = lons2[min_idx]
                to_add = tuple([coord_list['lat'], coord_list['long']])
                if to_add not in existing_lat_longs:
                    nearby_results.append(coord_list)
                    existing_lat_longs.add(to_add)
            
    else:

        lons2 = np.array([coord['long'] for coord in locations_coord['results']])
        lats2 = np.array([coord['lat'] for coord in locations_coord['results']])

        lons1 = np.array([long1] * len(lons2))
        lats1 = np.array([lat1] * len(lats2))
        geodesic = pyproj.Geod(ellps='WGS84')
        fwd_azimuth, back_azimuth, distance_m = geodesic.inv(
            lons1=lons1,
            lats1=lats1,
            lons2=lons2,
            lats2=lats2,
        )
        
        distance_km = distance_m / 1000.0

        nearby_results = []
        for i in range(len(locations_coord['results'])):
            coord = locations_coord['results'][i]
            coord['distance_km'] = distance_km[i]
            if distance_km[i] <= threshold:
                to_add = tuple([coord['lat'], coord['long']])
                if to_add not in existing_lat_longs:
                    nearby_results.append(coord)
                    existing_lat_longs.add(to_add)
    
    return nearby_results
