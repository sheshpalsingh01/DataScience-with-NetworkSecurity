from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger
from networksecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig,TrainingPipelineConfig,DataTransformationConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact
import sys
import os


if __name__ == "__main__":
    try:
        logger.info("Starting Training Pipeline...")
        trainingpipelineconfig = TrainingPipelineConfig()
        logger.info(f"Artifact Directory configured at: {trainingpipelineconfig.artifact_dir}")
        dataingestionconfig = DataIngestionConfig(training_pipeline_config=trainingpipelineconfig)
        data_ingestion = DataIngestion(data_ingestion_config=dataingestionconfig)
        logger.info("Starting Data Ingestion component...")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logger.info(f"Data Ingestion completed successfully. Artifact: {dataingestionartifact}")
        logger.info("Data Ingestion complate.......")
        print("="*50)
        print(dataingestionartifact)
        print("="*50)
        data_validation_config = DataValidationConfig(training_pipeline_config=trainingpipelineconfig)
        data_validation = DataValidation(data_ingestion_artifact=dataingestionartifact, data_validation_config=data_validation_config)
        logger.info("Starting Data Validation component...")
        data_validation_artifact = data_validation.initiate_data_validation()
        logger.info(f"Data Validation completed successfully. Artifact: {data_validation_artifact}")
        logger.info("Data Validation complete.......")
        print("="*50)
        print(data_validation_artifact)
        print("="*50)
        data_transformation_config = DataTransformationConfig(training_pipeline_config=trainingpipelineconfig)
        data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact, data_transformation_config=data_transformation_config)
        logger.info("Starting Data Transformation component...")
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logger.info(f"Data Transformation completed successfully. Artifact: {data_transformation_artifact}")
        logger.info("Data Transformation complate.......")
        print("="*50)
        print(data_transformation_artifact)
        print("="*50)
        

    except Exception as e:
        custom_exception = NetworkSecurityException(e, sys)
        logger.error(str(custom_exception))
        print(custom_exception)
        raise custom_exception from e 