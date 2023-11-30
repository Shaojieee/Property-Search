
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append('../')

import psycopg2
from data.return_nearby_amenities import valid_amenities

import os
from dotenv import load_dotenv
load_dotenv()



def calculate_property_amenities():
    threshold = 3.00
    table = 'property_amenities'

    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
        database=os.environ['OLAP_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )
    # Create a cursor object
    cur = conn.cursor()
    # Execute the TRUNCATE command
    cur.execute(f"TRUNCATE {table}")
    # Commit the transaction
    conn.commit()

    query = f'''
    INSERT INTO property_amenities (property_latitude, property_longitude, amenity_latitude, amenity_longitude, amenity_type, amenity_name, distance_km)
    select 
        *,
        calculate_distance(property_latitude, property_longitude, amenity_latitude, amenity_longitude) as distance_km
    from 
    (
    select
        p.latitude as property_latitude,
        p.longitude as property_longitude,
        a.latitude as amenity_latitude,
        a.longitude as amenity_longitude,
        a.type as amenity_type,
        a.name as amenity_name
    from 
    (
        select
            distinct
            p.latitude,
            p.longitude
        from 
            properties p 
    ) p
    cross join
        amenities a
    )
    where 
        calculate_distance(property_latitude, property_longitude, amenity_latitude, amenity_longitude) <= {threshold};
    '''
    cursor = conn.cursor() 
    try: 
        cursor.execute(query) 
        conn.commit() 
    except (Exception, psycopg2.DatabaseError) as error: 
        print("Error: %s" % error) 
        conn.rollback() 
        cursor.close() 
        return 1
    cursor.close() 

    conn.close()


def create_agg_property_table():
    table = 'properties_w_amenities'
    amenities = list(valid_amenities)
    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
        database=os.environ['OLAP_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )
    # Create a cursor object
    cur = conn.cursor()
    # Execute the TRUNCATE command
    cur.execute(f"TRUNCATE {table}")
    # Commit the transaction
    conn.commit()

    query = f'''
    INSERT INTO public.properties_w_amenities (id,"name",url,price,num_bedroom,num_bathroom,cost_psf,address,road_name,building,postal_code,latitude,longitude,floor_area,land_area,walk_destination,walk_distance_m,walk_time_mins,lease_duration,completion,"type",{",".join([f'has_{x}' for x in valid_amenities])})
    select
        p.id,
        p.name,
        p.url,
        p.price,
        p.num_bedroom,
        p.num_bathroom,
        p.cost_psf,
        p.address,
        p.road_name,
        p.building,
        p.postal_code,
        p.latitude,
        p.longitude,
        p.floor_area,
        p.land_area,
        p.walk_destination,
        p.walk_distance_m,
        p.walk_time_mins,
        p.lease_duration,
        p.completion,
        p.type,
        {",".join([f'd.has_{x}' for x in amenities])}
    from
        properties p 
    left join 
    (
        select 
            property_latitude,
            property_longitude,
            {",".join([f"cast(max(case when amenity_type='{x}' then 1 else 0 end) as boolean) as has_{x}" for x in amenities])}
        from 
            property_amenities
        group by 
            1,2
    ) d on p.latitude=d.property_latitude and p.longitude=d.property_longitude;
    '''
    cursor = conn.cursor() 
    try: 
        cursor.execute(query) 
        conn.commit() 
    except (Exception, psycopg2.DatabaseError) as error: 
        print("Error: %s" % error) 
        conn.rollback() 
        cursor.close() 
        return 1
    cursor.close() 

    conn.close()


if __name__=='__main__':
    import time
    start_time = time.time()
    calculate_property_amenities()
    end_time = time.time()

    print(f'Calculate Amenities Time: {end_time-start_time}')

    start_time = time.time()
    create_agg_property_table()
    end_time = time.time()

    print(f'Agg Property Time: {end_time-start_time}')