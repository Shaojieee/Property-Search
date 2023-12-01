#!/bin/bash

pyenv activate housing_proj
python ./data/pipeline_update_amenities/overall_pipeline.py
