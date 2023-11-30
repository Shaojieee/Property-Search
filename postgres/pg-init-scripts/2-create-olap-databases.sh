#!/bin/bash

set -e
set -u

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "olap" <<-EOSQL 
CREATE TABLE public.properties(id BIGINT PRIMARY KEY, name VARCHAR NOT NULL,url VARCHAR NOT NULL,price FLOAT,num_bedroom INT,num_bathroom INT,cost_psf FLOAT,address VARCHAR,road_name VARCHAR,building VARCHAR,postal_code INT,latitude FLOAT,longitude FLOAT,floor_area FLOAT,land_area FLOAT,walk_destination VARCHAR, walk_distance_m FLOAT, walk_time_mins FLOAT, lease_duration VARCHAR,completion INT,type VARCHAR, has_secondary_school BOOLEAN,has_hawker BOOLEAN,has_disability_service BOOLEAN,has_preschool BOOLEAN,has_cycling_path BOOLEAN,has_sport_facility BOOLEAN,has_npark BOOLEAN,has_childcare BOOLEAN,has_kindergarten BOOLEAN,has_eldercare BOOLEAN,has_mall BOOLEAN,has_primary_school BOOLEAN,has_college BOOLEAN);
CREATE TABLE public.amenities ("type" varchar NOT NULL,"name" varchar NOT NULL,latitude varchar NOT NULL,longitude varchar NOT NULL, CONSTRAINT amenities_pkey PRIMARY KEY (type, name, latitude, longitude);
);CREATE TABLE public.property_amenities(property_id BIGINT, amenity_type VARCHAR NOT NULL, amenity_name VARCHAR NOT NULL, latitude FLOAT NOT NULL, longitude FLOAT NOT NULL, distance_km FLOAT, PRIMARY KEY (property_id, amenity_type, amenity_name, latitude, longitude), FOREIGN KEY (property_id) REFERENCES properties (id));
CREATE OR REPLACE FUNCTION public.calculate_distance(lat_1 double precision, long_1 double precision, lat_2 double precision, long_2 double precision) RETURNS double precision LANGUAGE plpgsql AS $function$ DECLARE dist float = 0;radlat_1 float;radlat_2 float;theta float;radtheta float;BEGIN IF lat_1 = lat_2 AND long_1 = long_2 THEN RETURN dist; ELSE radlat_1 = pi() * lat_1 / 180;radlat_2 = pi() * lat_2 / 180;theta = long_1 - long_2;radtheta = pi() * theta / 180;dist = sin(radlat_1) * sin(radlat_2) + cos(radlat_1) * cos(radlat_2) * cos(radtheta);IF dist > 1 THEN dist = 1; END IF;dist = acos(dist);dist = dist * 180 / pi();dist = dist * 60 * 1.1515;dist = dist * 1.609344; RETURN dist;END IF;END;$function$;
GRANT ALL ON SCHEMA public TO olap;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO olap;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO olap;
GRANT ALL ON ALL TABLES IN SCHEMA public TO olap;
EOSQL
