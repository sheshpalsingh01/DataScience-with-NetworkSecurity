from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger
from networksecurity.entity.config_entity import DataIngestionConfig,TrainingPipelineConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

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
        print(dataingestionartifact)

    except Exception as e:
        custom_exception = NetworkSecurityException(e, sys)
        logger.error(str(custom_exception))
        print(custom_exception)
        raise custom_exception from e 