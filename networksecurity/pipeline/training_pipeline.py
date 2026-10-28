import os
import sys
from dotenv import load_dotenv

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.cloud.s3_sync import S3Sync
from networksecurity.logging.logger import logger
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.entity.config_entity import ModelTrainerConfig, DataIngestionConfig, DataTransformationConfig,DataValidationConfig,TrainingPipelineConfig
from networksecurity.entity.artifact_entity import (
    ModelTrainerArtifact,
    DataTransformationArtifact,
    DataIngestionArtifact,
    DataValidationArtifact, 
)

class TrainingPipeline:
    def __init__(self):
        load_dotenv()
        self.training_pipeline_config = TrainingPipelineConfig()
        self.training_bucket_name = os.getenv("TRAINING_BUCKET_NAME")
        self.s3_sync = S3Sync() if self.training_bucket_name else None

    def start_data_ingestion(self):
        try:
            self.data_ingestion_config= DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logger.info("Iniate data ingestion ..................")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact= data_ingestion.initiate_data_ingestion()
            logger.info("Data ingestion completed successfully")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact):
        try:
            self.data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            logger.info("Initiate data validation ........................")
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact, data_validation_config=self.data_validation_config)
            data_validation_artifact = data_validation.initiate_data_validation()
            logger.info("Data validation completed successfully")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact):
        try:
            self.data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            logger.info("Initiate data transformation ........................")
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact, data_transformation_config=self.data_transformation_config)
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logger.info("Data transformation completed successfully")
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    

    def start_model_training(self,model_transformation_artifact:DataTransformationArtifact)->ModelTrainerArtifact:
        try:
            self.model_trainer_config:ModelTrainerConfig = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            logger.info("Initiate model training ........................")
            model_trainer = ModelTrainer(data_transformation_artifact=model_transformation_artifact, model_trainer_config=self.model_trainer_config)
            model_trainer_artifact = model_trainer.initiate_model_training()
            logger.info("Model training completed successfully")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def sync_artifact_dir_to_s3(self):
        try:
            if not self.training_bucket_name or not self.s3_sync:
                raise ValueError("Set TRAINING_BUCKET_NAME to enable S3 artifact uploads.")
            aws_bucket_url = (
                f"s3://{self.training_bucket_name}/artifacts/"
                f"{self.training_pipeline_config.timestamp}"
            )
            self.s3_sync.sync_folder_to_s3(
                folder=self.training_pipeline_config.artifact_dir,
                aws_bucket_url=aws_bucket_url,
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def sync_saved_model_dir_to_s3(self):
        try:
            if not self.training_bucket_name or not self.s3_sync:
                raise ValueError("Set TRAINING_BUCKET_NAME to enable S3 model uploads.")
            aws_bucket_url = (
                f"s3://{self.training_bucket_name}/final_model/"
                f"{self.training_pipeline_config.timestamp}"
            )
            self.s3_sync.sync_folder_to_s3(
                folder=self.training_pipeline_config.model_dir,
                aws_bucket_url=aws_bucket_url,
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_training(model_transformation_artifact=data_transformation_artifact)
            if self.training_bucket_name:
                self.sync_artifact_dir_to_s3()
                self.sync_saved_model_dir_to_s3()
            else:
                logger.info(
                    "S3 sync is disabled; set TRAINING_BUCKET_NAME to enable it."
                )
            return model_trainer_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e,sys)