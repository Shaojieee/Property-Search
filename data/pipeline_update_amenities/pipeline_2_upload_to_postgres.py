import json
import os

import psycopg2
import psycopg2.extras as extras

import pandas as pd
from data.return_nearby_amenities import valid_amenities

from dotenv import load_dotenv
load_dotenv()

def upload_amenities(input_dir):
    table = 'amenities'

    
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

    files = [os.path.join(input_dir, x) for x in os.listdir(input_dir) if x!='.DS_Store']

    for amenity in valid_amenities:
        input_file = os.path.join(input_dir, amenity+'_coords.json')

        with open(input_file, 'r') as f:
            data = json.load(f)

        data = data['results']

        df = pd.DataFrame(data)
        df['type'] = amenity
        df['name'] = df['name'].astype(str)
        df = df.rename(columns={'lat':'latitude', 'long':'longitude'})
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)

        df = df.drop_duplicates()
        execute_values(conn, df, 'amenities')
    conn.close()

        

def execute_values(conn, df, table): 
  
    tuples = [tuple(x) for x in df.to_numpy()] 
    cols = ','.join(list(df.columns)) 
    cols_excluded = ', '.join([f'{col} = EXCLUDED.{col}' for col in list(df.columns)])
    # SQL query to execute 
    query = '''
    INSERT INTO 
        %s(%s) 
    VALUES 
    %%s
    ''' % (table, cols) 
    cursor = conn.cursor() 
    try: 
        extras.execute_values(cursor, query, tuples) 
        conn.commit() 
    except (Exception, psycopg2.DatabaseError) as error: 
        print("Error: %s" % error) 
        conn.rollback() 
        cursor.close() 
        return 1
    cursor.close() 
