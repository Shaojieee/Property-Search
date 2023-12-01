# Property Location Search

## Setup

1. Installing required Python packages from `requirements.txt`
2. Install Docker Engine and Docker Compose
3. Register an OneMap account to access the API endpoints 

## Initialisation (Tested on MacOS)

1. Run the following command to initialise the PostgreSQL database and load data into into the database. This will take approximately 10 mins as we are writing large amounts of data into database. Also do ensure that the PostgreSQL

    ```
    chmod +x initialise.sh

    bash initialise.sh
    ```

2. Under the `.env` file, fill in your OneMap API credentials.

    ```
    ONE_MAP_API_EMAIL={one_map_email}
    ONE_MAP_API_PASSWORD={one_map_password}
    ```

3. Run the streamlit dashboard to get started!

    ```
    streamlit run ./streamlit/Homepage.py
    ```

## Pipelines
Under the `./data` folder, there are 3 subfolders for 3 different pipelines. Please ensure that the PostgreSQL database is properly set up and running before running any of the pipelines.

1. `./data/pipeline_first_time`
    
    This pipeline contains notebooks that we use to obtain the first batch of data. Running the notebook here requires a lot of time and manual inputs due to the large number of listings and the bot prevention capabilities on Property Guru.

2. `./data/pipeline_update_amenities/overall_pipeline.py`

    This pipeline is created to periodically fetch the amenities from OneMap Search API and upload the data onto PostgreSQL. After uploading the data, we need to recomputate the nearby amenities for each property in Postgres.

    We recommend to schedule this script to run once every week `15 */5 * * 7` as amenities do not change frequently.

3. `./data/pipeline_update_listings/overall_pipeline.py`

    This pipeline is created to fetch, process and upload the latest property listings on Property Guru periodically. 

    Due to the bot prevention capabilities on Property Guru, we are only able to retrieve 10 pages of new properties every single time before running into a reCAPTCHA. Hence we recommend to run this pipeline every 15 minutes `*/15 * * * *` to ensure that we do not miss out on any new listings.


## Data
Our data are stored in the `./data/data` folder.

1. `./data/data/raw/unprocessed`

    This folder is partitions by the time of information retrieval and consist of the raw html files that we obtain from Property Guru. 
    
    **_NOTE:_** We only keep a 20 out of 2,400 html files that we retrieve during the first mass retrieval from Property Guru. However, this data has been processed and the aggregated form can be found the folders mentioned below.

2. `./data/data/raw/processed`

    This folder is partitions by the time of information retrieval and consist of the raw information extracted from the html files that we obtain from Property Guru.

3. `./data/data/processed`

    This folder is partitions by the time of information retrieval and consist of the clean and processed information extracted from the html files that we obtain from Property Guru.