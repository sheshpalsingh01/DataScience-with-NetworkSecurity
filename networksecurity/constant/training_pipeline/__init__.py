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

SCHEMA_FILE_PATH = os.path.join("data_schema","schema.yaml")


"""
Data Ingestin related contstsnt start with DATA_INGESTION VAR NAME

"""
DATA_INGESTION_COLLECTION_NAME: str = "phisingData"
DATA_INGESTION_DATABASE_NAME:str = "sheshpalsingh"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested_data"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION: float = 0.2


"""
Data Validation related contstsnt start with DATA_VALIDATION VAR NAME

"""
DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_VALID_DIR: str = "validated"
DATA_VALIDATION_INVALID_DIR: str = "invalid_data"
DATA_VALIDATION_DRIFT_REPORT_DIR: str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.yaml"
