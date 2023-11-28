#!/bin/bash

set -e
set -u

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "olap" <<-EOSQL 
CREATE TABLE public.properties( id INT PRIMARY KEY, name VARCHAR NOT NULL,url VARCHAR NOT NULL,price FLOAT NOT NULL,num_bedroom INT,num_bathroom INT,cost_psf FLOAT,address VARCHAR,road_name VARCHAR,building VARCHAR,postal_code INT,latitude FLOAT,longitude FLOAT,floor_area FLOAT,land_area FLOAT,lease_duration VARCHAR,type VARCHAR);
GRANT ALL ON SCHEMA public TO olap;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO olap;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO olap;
GRANT ALL ON ALL TABLES IN SCHEMA public TO olap;
EOSQL
