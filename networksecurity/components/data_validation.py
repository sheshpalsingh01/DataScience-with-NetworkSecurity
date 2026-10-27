# pyrefly: ignore[missing-import]
import os
import sys
from typing import Tuple
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
)
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file


class DataValidation:
    def __init__(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_config: DataValidationConfig,
    ):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            logger.info(f"Reading CSV file from: {file_path}")
            dataframe = pd.read_csv(file_path)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self.schema_config["columns"])
            logger.info(f"Required number of columns: {number_of_columns}")
            logger.info(f"Dataframe has {len(dataframe.columns)} columns")
            if len(dataframe.columns) == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def check_numerical_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            logger.info("Checking numerical columns against schema...")
            numerical_columns = list(self.schema_config["numerical_columns"])
            dataframe_columns = list(dataframe.columns)
            missing_numerical_columns = list(
                set(numerical_columns) - set(dataframe_columns)
            )
            if len(missing_numerical_columns) == 0:
                logger.info("All numerical columns are present in dataframe.")
                return True
            logger.error(f"Missing numerical columns: {missing_numerical_columns}")
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(
        self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold: float = 0.05
    ) -> Tuple[bool, dict]:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                c1 = current_df[column]
                is_sample_dist = ks_2samp(d1, c1)

                if threshold <= is_sample_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False

                report.update(
                    {
                        column: {
                            "drift_status": is_found,
                            "p_value": float(is_sample_dist.pvalue),
                        }
                    }
                )

            drift_report_file_path = self.data_validation_config.drift_report_file_path

            # creating directory
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)

            write_yaml_file(file_path=drift_report_file_path, content=report)
            logger.info(f"Drift report saved at: {drift_report_file_path}")

            return status, report

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            # Read the data train and test
            logger.info("Reading train and test datasets for validation...")
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            # Validate number of columns
            train_status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not train_status:
                error_message = "Train dataframe does not contain all required columns."
                logger.error(error_message)
                raise Exception(error_message)

            test_status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not test_status:
                error_message = "Test dataframe does not contain all required columns."
                logger.error(error_message)
                raise Exception(error_message)

            # Check numerical columns
            train_num_status = self.check_numerical_columns(dataframe=train_dataframe)
            if not train_num_status:
                error_message = "Train dataframe is missing numerical columns."
                logger.error(error_message)
                raise Exception(error_message)

            test_num_status = self.check_numerical_columns(dataframe=test_dataframe)
            if not test_num_status:
                error_message = "Test dataframe is missing numerical columns."
                logger.error(error_message)
                raise Exception(error_message)

            # Check dataset drift
            logger.info("Detecting dataset drift between train and test datasets...")
            drift_status, report = self.detect_dataset_drift(
                base_df=train_dataframe, current_df=test_dataframe
            )

            # Create directory and save validated datasets
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )
            logger.info(f"Saved validated train data to: {self.data_validation_config.valid_train_file_path}")
            logger.info(f"Saved validated test data to: {self.data_validation_config.valid_test_file_path}")

            data_validation_artifact = DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            logger.info(f"Data Validation completed successfully. Artifact: {data_validation_artifact}")
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # Alias for backward compatibility if misspelled method is called
    # initiate_data_valedation = initiate_data_validation
