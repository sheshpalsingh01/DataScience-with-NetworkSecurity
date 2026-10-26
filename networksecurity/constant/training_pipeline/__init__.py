import os
import sys
import numpy as np
import pandas as pd 

"""
Defining common constants for training pipeline
"""
TARGET_COLUMN = "Result"
PIPELINE_NAME : str ="networksecurity"
PIPELINE_ARTIFACT_DIR: str = "artifacts"
FILE_NAME :str = "phisingData.csv"

TRAIN_FILE_NAME:str = "train.csv"
TEST_FILE_NAME:str = "test.csv"



"""
Data Ingestin related contstsnt start with DATA_INGESTION VAR NAME

"""
DATA_INGESTION_COLLECTION_NAME: str = "phisingData"
DATA_INGESTION_DATABASE_NAME:str = "sheshpalsingh"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested_data"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION: float = 0.2
