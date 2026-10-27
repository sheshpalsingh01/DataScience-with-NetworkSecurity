from networksecurity.constant import training_pipeline
from networksecurity.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS, TARGET_COLUMN
from networksecurity.utils.main_utils.utils import save_object,load_object, save_numpy_array
from networksecurity.logging.logger import logger
import os,sys
import numpy as np
import pandas as pd 
from sklearn.imputer import KNNImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from networksecurity.utils.utils import save_object,load_object


class DataTransformation:
    ...
    