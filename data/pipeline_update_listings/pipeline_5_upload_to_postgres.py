import pandas as pd
import numpy as np
import psycopg2
import psycopg2.extras as extras

import os
from dotenv import load_dotenv
load_dotenv()




def upsert_to_postgres(input_file, table):
    psycopg2.extensions.register_adapter(float, nan_to_null)

    df = pd.read_csv(input_file)
    
    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
        database=os.environ['OLAP_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )

    execute_values(conn, df, table)

def nan_to_null(f,
        _NULL=psycopg2.extensions.AsIs('NULL'),
        _Float=psycopg2.extensions.Float):
    if not np.isnan(f):
        return _Float(f)
    return _NULL


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
    ON CONFLICT ON CONSTRAINT %s DO UPDATE
    SET %s;
    ''' % (table, cols, f'{table}_pkey', cols_excluded) 
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