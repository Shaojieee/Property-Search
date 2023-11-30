import pandas as pd
import json
from tqdm import tqdm
import math

from return_nearby_amenities import search_nearby_amenities, valid_amenities


def generate_amenities(input_file, output_listings_file, output_amenities_file):

    listings = pd.read_csv(input_file)

    amenities = {
        'property_id': [],
        'amenity_type': [],
        'amenity_name': [],
        'latitude': [],
        'longitude': [],
        'distance_km': [],
    }

    for amenity in valid_amenities:
        print(amenity)
        listings[f'has_{amenity}'] = False
        for i, row in listings.iterrows():
            if math.isnan(row['latitude']):
                continue
            
            results = search_nearby_amenities(
                lat1=row['latitude'],
                long1=row['longitude'],
                type=amenity,
                threshold=3
            )

            listings.at[i, f'has_{amenity}'] = (len(results)>0)
            for result in results:
                amenities['property_id'].append(row['id'])
                amenities['amenity_type'].append(amenity)
                amenities['amenity_name'].append(result['name'])
                amenities['latitude'].append(result['lat'])
                amenities['longitude'].append(result['long'])
                amenities['distance_km'].append(result['distance_km'])
    
    amenities_df = pd.DataFrame(amenities)

    amenities_df.to_csv(output_amenities_file, index=False)

    listings.to_csv(output_listings_file, index=False)