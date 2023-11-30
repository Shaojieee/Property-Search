import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append('../../')

import datetime
from dateutil import tz
from data.pipeline_update_listings.pipeline_1_scrape_updated_search_results_page import scrape_latest_results
from data.pipeline_update_listings.pipeline_2_extract_search_results import extract_listings
from data.pipeline_update_listings.pipeline_3_process_search_results import process_search_results
from data.pipeline_update_listings.pipeline_4_generate_amenities import generate_amenities
from data.pipeline_update_listings.pipeline_5_upload_to_postgres import upsert_to_postgres
from data.postgres_calculate_amenities import create_agg_property_table



def overall_pipeline():
    cur_datetime = datetime.datetime.now(tz=tz.gettz('Asia/Singapore')).strftime('%Y%m%d%H%M')
    unprocessed_dir = f'../data/raw/unprocessed/{cur_datetime}'
    raw_processed_dir = f'../data/raw/processed/{cur_datetime}'
    raw_processed_output_file = os.path.join(raw_processed_dir, 'raw_extracted.json')

    processed_dir = f'../data/processed/{cur_datetime}'
    processed_file = os.path.join(processed_dir, 'processed.csv')
    amenities_file = os.path.join(processed_dir, 'property_amenities.csv')
    processed_file_w_amenities = os.path.join(processed_dir, 'processed_w_amenities.csv')

    onemap_search_db = './data/one_map_search_results_db.json'

    

    # Step 1: Scrape recent listings from property guru
    os.makedirs(unprocessed_dir, exist_ok=True)
    scrape_latest_results(
        output_dir=unprocessed_dir
    )

    # Step 2: Extract information from raw html file
    os.makedirs(raw_processed_dir, exist_ok=True)
    extract_listings(
        input_dir=unprocessed_dir,
        output_file=raw_processed_output_file
    )

    # Step 3: Clean and process the data
    os.makedirs(processed_dir, exist_ok=True)
    process_search_results(
        input_file=raw_processed_output_file,
        output_file=processed_file,
        onemap_search_db=onemap_search_db
    )

    # Step 4: Generate amenities for properties
    generate_amenities(
        input_file=processed_file,
        output_amenities_file=amenities_file,
        output_listings_file=processed_file_w_amenities,
    )

    # Step 5: Upsert data to postgres
    upsert_to_postgres(
        input_file=processed_file_w_amenities,
        table='properties'
    )

    upsert_to_postgres(
        input_file=amenities_file,
        table='property_amenities'
    )

    # Step 6: Update the aggregated table
    create_agg_property_table()
    


if __name__=='__main__':
    overall_pipeline()