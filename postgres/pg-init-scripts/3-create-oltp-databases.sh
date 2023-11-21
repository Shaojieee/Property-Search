#!/bin/bash

set -e
set -u

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "oltp"<<-EOSQL 
    CREATE TABLE public.logs (id serial PRIMARY KEY,run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE public.locations(runs_id INT NOT NULL,name VARCHAR NOT NULL,lat FLOAT NOT NULL,long FLOAT NOT NULL,travel_type VARCHAR(50) NOT NULL,frequency INT NOT NULL,PRIMARY KEY (runs_id, lat, long),FOREIGN KEY (runs_id) REFERENCES logs (id));
    GRANT ALL ON SCHEMA public TO oltp;
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO oltp;
    GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO oltp;
    GRANT ALL ON ALL TABLES IN SCHEMA public TO oltp;
EOSQL
