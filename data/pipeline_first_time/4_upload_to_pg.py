import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
sys.path.append('../../')

import pandas as pd
import numpy as np
import psycopg2
import psycopg2.extras as extras

from dotenv import load_dotenv
load_dotenv()


def nan_to_null(f,
        _NULL=psycopg2.extensions.AsIs('NULL'),
        _Float=psycopg2.extensions.Float):
    if not np.isnan(f):
        return _Float(f)
    return _NULL

def execute_values(conn, df, table): 
  
    tuples = [tuple(x) for x in df.to_numpy()] 
  
    cols = ','.join(list(df.columns)) 
    # SQL query to execute 
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols) 
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

def first_time_upload():
    psycopg2.extensions.register_adapter(float, nan_to_null)


    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
        database=os.environ['OLAP_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )


    final = pd.read_csv('../data/processed/20231116/processed.csv')

    columns = [
        'id','name','url','price','num_bedroom','num_bathroom','cost_psf',
        'address','road_name','building','postal_code','latitude','longitude',
        'floor_area','land_area','walk_destination','walk_distance_m','walk_time_mins',
        'lease_duration','completion','type',
    ]
    properties = final[columns]

    execute_values(conn, properties, 'properties')


if __name__=='__main__':
    first_time_upload()