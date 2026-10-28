from networksecurity.constant import training_pipeline
from networksecurity.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS, TARGET_COLUMN
from networksecurity.utils.main_utils.utils import save_object, load_object, save_numpy_array
from networksecurity.logging.logger import logger
import os, sys
import numpy as np
import pandas as pd 
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline


class DataTransformation:
    def __init__(self, data_validation_artifact:DataValidationArtifact,
                data_transformation_config:DataTransformationConfig):
                try:
                   self.data_validation_artifact:DataValidationArtifact=data_validation_artifact
                   self.data_transformation_config:DataTransformationConfig=data_transformation_config

                except Exception as e:
                    raise NetworkSecurityException(e,sys)

    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def get_data_transformer_object(self)->Pipeline:
        """
            It initialies a KNNImputer object with the parameters specified in the training_pipeline.py file
            and return a Pipeline object with the KNNImputer object as the first step.
            Args:
            cls: Data Transformation object
            Returns:
            Pipeline: Pipeline object

        """  
        logger.info("Enter get data transformer object method")
        try:
            imputer:KNNImputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)             
            logger.info(f"Initialse KNNImputer object with parameters : {DATA_TRANSFORMATION_IMPUTER_PARAMS}")
            
            processor:Pipeline= Pipeline(steps=[
                ('imputer',imputer)
            ])
            
            logger.info("Returning Data Transformer Object")
            return processor
            

        except Exception as e:
            raise NetworkSecurityException(e,sys)

    

    def initiate_data_transformation(self)->DataTransformationArtifact:
        logger.info("Initiating Data Transformation")
        try:
            logger.info("Loading training and test data")
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            #training dataframe split
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN])
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1,0)

            #testing dataframe split
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN])
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1,0)

            preprocessor = self.get_data_transformer_object()

            preprocessor_object = preprocessor.fit(input_feature_train_df)

            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)

            train_arr = np.c_[transformed_input_train_feature,np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature,np.array(target_feature_test_df)]


            ## Save th numpy array data
            save_numpy_array(file_path=self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array(file_path=self.data_transformation_config.transformed_test_file_path,array=test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path,preprocessor_object)
            save_object("final_model/preprocessor.pkl",preprocessor_object)

            ## Preparing for artifact
            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

            logger.info("Data transformation completed successfully")
            return data_transformation_artifact
            

        except Exception as e:
            raise NetworkSecurityException(e,sys)


    