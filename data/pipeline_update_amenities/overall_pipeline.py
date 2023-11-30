import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
sys.path.append('../../')

import psycopg2

from data.pipeline_update_amenities.pipeline_1_gathering_from_onemap import *
from data.pipeline_update_amenities.pipeline_2_upload_to_postgres import upload_amenities
from data.postgres_calculate_amenities import calculate_property_amenities, create_agg_property_table

from dotenv import load_dotenv
load_dotenv()

def overall_pipeline():
    output_dir = '../amenities'
    os.makedirs(output_dir, exist_ok=True)

    get_childcare(
        output_dir=output_dir
    )

    get_college(
        output_dir=output_dir
    )

    get_disability_service(
        output_dir=output_dir
    )

    get_eldercare(
        output_dir=output_dir
    )

    get_hawker(
        output_dir=output_dir
    )

    get_kindergarten(
        output_dir=output_dir
    )

    get_malls(
        output_dir=output_dir
    )

    get_nparks(
        output_dir=output_dir
    )

    get_preschool(
        output_dir=output_dir
    )

    get_primary_school(
        output_dir=output_dir
    )

    get_secondary_school(
        output_dir=output_dir
    )

    get_sports_facility(
        output_dir=output_dir
    )

    get_cycling_path(
        output_dir=output_dir
    )

    
    upload_amenities(
        input_dir=output_dir
    )


    calculate_property_amenities()

    create_agg_property_table()


if __name__=='__main__':
    overall_pipeline()