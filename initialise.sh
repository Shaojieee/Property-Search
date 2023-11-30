#! /bin/bash

cd ./postgres
# Set up docker container
docker compose up -d

sleep 60

echo "Uploading properties"
# Upload properties into postgres
cd ../
python ./data/pipeline_first_time/4_upload_to_pg.py

# Upload amenities 
echo "Starting amenities pipeline"  
python ./data/pipeline_update_amenities/overall_pipeline.py


