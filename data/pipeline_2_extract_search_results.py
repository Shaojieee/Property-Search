import os
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import pandas as pd
import re


def extract_listings(input_dir, output_file):
    files = [os.path.join(input_dir, x) for x in os.listdir(input_dir) if x!='.DS_Store']
    store = {}
    dups = set()
    for file in tqdm(files):
        try:
            with open(file, 'r') as f:
                page = BeautifulSoup(f, 'html.parser')
        except:
            print(file)
            break
        listings = page.find_all(name='div', attrs={'class': 'listing-card'})
        for listing in listings:
            info = {
                'name': None, 
                'url': None, 
                'street_address': None, 
                'price': None, 
                'num_bedroom': None, 
                'num_bathroom': None, 
                'cost_psf': None, 
                'total_area': None,
                'walk': None,
                'tags': None,
                'recency': None,
            }
            property_guru_id = listing.get('data-listing-id')

            listing = listing.find(name='div', attrs={'class':'listing-description'})

            info['name'] = listing.find(name='a', attrs={'itemprop':'url'}).text
            info['url'] = listing.find(name='a', attrs={'itemprop':'url'}).get('href')

            info['street_address'] = listing.find(name='span', attrs={'itemprop':'streetAddress'}).text

            info['price'] = listing.find(name='li', attrs={'data-automation-id': 'listing-card-price-txt'}).text

            other_details = listing.find(name='ul', attrs={'data-automation-id': 'listing-card-other-details-txt'})

            num_bedroom = other_details.find(name='span', attrs={'class':'bed'})
            if num_bedroom:
                info['num_bedroom'] = num_bedroom.text
            
            num_bathroom = other_details.find(name='span', attrs={'class':'bath'})
            if num_bathroom:
                info['num_bathroom'] = num_bathroom.text

            floor_details = other_details.find_all(name='li', attrs={'class': 'listing-floorarea'})

            for floor in floor_details:
                text = floor.text.strip()
                if 'psf' in text:
                    info['cost_psf'] = text
                elif 'sqft' in text:
                    info['total_area'] = text
            
            walk = listing.find(name='ul', attrs={'data-automation-id':'listing-card-features-walk'})
            if walk:
                info['walk'] = walk.text

            section = listing.find(name='div', attrs={'data-automation-id':'listing-card-tags'})
            tags = section.find(name='ul', attrs={'class': 'listing-property-type'})
            tags = tags.find_all(name='li')
            info['tags'] = [x.text for x in tags]

            info['recency'] = section.find(name='div', attrs={'class': 'listing-recency'}).text
            

            if property_guru_id in store:
                if info['url']!=store[property_guru_id]['url']:
                    dups.add(property_guru_id)
            else:
                store[property_guru_id] = info
    
    with open(output_file, 'w') as f:
        json.dump(store, f)