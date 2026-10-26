# pyrefly: ignore[missing-import]
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger
import os
import sys
import numpy as np
import pandas as pd
from typing import List
import pymongo

# Configation of the data ingestion Config

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGODB_URI")


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
            logger.info("Initializing DataIngestion component with provided configuration.")
        except Exception as e:
            logger.error(f"Error in initializing DataIngestion: {e}")
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self):
        """
        Export mongo db as dataframe
        """
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            logger.info(f"Connecting to MongoDB and fetching collection '{collection_name}' from database '{database_name}'")
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database_name][collection_name]
            dataframe = pd.DataFrame(list(collection.find()))
            logger.info(f"Extracted {len(dataframe)} records from MongoDB")

            if "_id" in dataframe.columns.to_list():
                dataframe = dataframe.drop("_id", axis=1)

            dataframe.replace({"nan": np.nan}, inplace=True)
            dataframe.replace({"null": np.nan}, inplace=True)
            logger.info(f"Preprocessed DataFrame shape: {dataframe.shape}")
            return dataframe

        except Exception as e:
            logger.error(f"Error in export_collection_as_dataframe: {e}")
            raise NetworkSecurityException(e, sys)

    def export_data_info_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            # creating folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Exporting raw data to feature store path: {feature_store_file_path}")
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            logger.info(f"Feature store export completed successfully at: {feature_store_file_path}")
            return dataframe
        except Exception as e:
            logger.error(f"Error in export_data_info_feature_store: {e}")
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            logger.info(f"Splitting data into train and test sets with ratio: {self.data_ingestion_config.train_test_split_ratio}")
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
           
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            logger.info(f"Saving train dataset (shape: {train_set.shape}) to: {self.data_ingestion_config.training_file_path}")
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            logger.info(f"Saving test dataset (shape: {test_set.shape}) to: {self.data_ingestion_config.testing_file_path}")
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            logger.info("Train-test split and file export completed successfully.")
            return train_set, test_set


        except Exception as e:
            logger.error(f"Error in split_data_as_train_test: {e}")
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self):
        try:
            logger.info("Initiating Data Ingestion workflow...")
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_info_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataIngestionartifact = DataIngestionArtifact(
                train_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            logger.info(f"Data Ingestion completed successfully. Artifact: {dataIngestionartifact}")
            return dataIngestionartifact

        except Exception as e:
            logger.error(f"Error in initiate_data_ingestion: {e}")
            raise NetworkSecurityException(e, sys)
