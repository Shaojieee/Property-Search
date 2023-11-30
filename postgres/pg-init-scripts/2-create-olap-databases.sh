#!/bin/bash

set -e
set -u


psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "olap" <<-EOSQL 
CREATE TABLE public.amenities ("type" varchar NOT NULL,"name" varchar NOT NULL,latitude float8 NOT NULL,longitude float8 NOT NULL,CONSTRAINT amenities_pkey PRIMARY KEY (type, name, latitude, longitude));
CREATE TABLE public.properties (id int8 NOT NULL,"name" varchar NOT NULL,url varchar NOT NULL,price float8 NULL,num_bedroom int4 NULL,num_bathroom int4 NULL,cost_psf float8 NULL,address varchar NULL,road_name varchar NULL,building varchar NULL,postal_code int4 NULL,latitude float8 NULL,longitude float8 NULL,floor_area float8 NULL,land_area float8 NULL,walk_destination varchar NULL,walk_distance_m float8 NULL,walk_time_mins float8 NULL,lease_duration varchar NULL,completion int4 NULL,"type" varchar NULL,CONSTRAINT properties_pkey PRIMARY KEY (id));
CREATE TABLE public.properties_w_amenities (id int8 NOT NULL,"name" varchar NOT NULL,url varchar NOT NULL,price float8 NULL,num_bedroom int4 NULL,num_bathroom int4 NULL,cost_psf float8 NULL,address varchar NULL,road_name varchar NULL,building varchar NULL,postal_code int4 NULL,latitude float8 NULL,longitude float8 NULL,floor_area float8 NULL,land_area float8 NULL,walk_destination varchar NULL,walk_distance_m float8 NULL,walk_time_mins float8 NULL,lease_duration varchar NULL,completion int4 NULL,"type" varchar NULL,has_secondary_school bool NULL,has_hawker bool NULL,has_disability_service bool NULL,has_preschool bool NULL,has_cycling_path bool NULL,has_sport_facility bool NULL,has_npark bool NULL,has_childcare bool NULL,has_kindergarten bool NULL,has_eldercare bool NULL,has_mall bool NULL,has_primary_school bool NULL,has_college bool NULL,CONSTRAINT properties_w_amenities_pkey PRIMARY KEY (id),CONSTRAINT properties_w_amenities_fk FOREIGN KEY (id) REFERENCES public.properties(id) ON DELETE CASCADE);
CREATE TABLE public.property_amenities (amenity_type varchar NOT NULL,amenity_name varchar NOT NULL,amenity_latitude float8 NOT NULL,amenity_longitude float8 NOT NULL,distance_km float8 NOT NULL,property_latitude float8 NOT NULL,property_longitude float8 NOT NULL,CONSTRAINT property_amenities_pkey PRIMARY KEY (amenity_type, amenity_name, amenity_latitude, amenity_longitude, property_latitude, property_longitude));
CREATE OR REPLACE FUNCTION public.calculate_distance(lat_1 double precision, long_1 double precision, lat_2 double precision, long_2 double precision) RETURNS double precision LANGUAGE plpgsql AS \$function\$ DECLARE dist float = 0;radlat_1 float;radlat_2 float;theta float;radtheta float;BEGIN IF lat_1 = lat_2 AND long_1 = long_2 THEN RETURN dist; ELSE radlat_1 = pi() * lat_1 / 180;radlat_2 = pi() * lat_2 / 180;theta = long_1 - long_2;radtheta = pi() * theta / 180;dist = sin(radlat_1) * sin(radlat_2) + cos(radlat_1) * cos(radlat_2) * cos(radtheta);IF dist > 1 THEN dist = 1; END IF;dist = acos(dist);dist = dist * 180 / pi();dist = dist * 60 * 1.1515;dist = dist * 1.609344; RETURN dist;END IF;END;\$function\$;
GRANT ALL ON SCHEMA public TO olap;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO olap;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO olap;
GRANT ALL ON ALL TABLES IN SCHEMA public TO olap;
EOSQL
