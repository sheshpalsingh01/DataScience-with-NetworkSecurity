from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV
import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger
import os, sys
import numpy as np
import dill 
import pickle


def read_yaml_file(file_path:str)->dict:
    try:
        with open(file_path,'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e,sys)

def write_yaml_file(file_path:str,content:object,replace:bool=False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                logger.info(f"file is already exist")
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path,'w') as yaml_file:
            yaml.dump(content,yaml_file)
    
    except Exception as e:
        raise NetworkSecurityException(e,sys)
        
        
def save_numpy_array(file_path:str,array:np.array):
    """
    Save numpy array data to file
    file_path : str location of the file
    array: np.array data array to save
    """
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        with open(file_path,'wb') as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise NetworkSecurityException(e,sys)

def load_numpy_array(file_path:str) -> np.array:
    """
    Load numpy array data from file
    file_path : str location of the file
    array: np.array data array to load
    """
    try:
        with open(file_path,'rb') as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys)

def save_object(file_path:str,obj:object):
    """
    Save object data to file
    file_path : str location of the file
    obj: object data to save
    """
    try:
        logger.info("Enter the savr_object method of main utils")
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        with open(file_path,'wb') as file_obj:
            pickle.dump(obj,file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys)


def load_object(file_path:str) -> object:
    """
    Load object data from file
    file_path : str location of the file
    obj: object data to load
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"file not found at {file_path}")
        with open(file_path,'rb') as file_obj:
            logger.info(f"loading object from {file_path}")
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys)


def evaluate_models(x_train, y_train, x_test, y_test, models, param):
    try:
        report = {}

        for i in range(len(list(models))):
            model_name = list(models.keys())[i]
            model = list(models.values())[i]
            para = param.get(model_name, {})

            gs = GridSearchCV(model, para, cv=3)
            gs.fit(x_train, y_train)

            model.set_params(**gs.best_params_)
            model.fit(x_train, y_train)

            y_train_pred = model.predict(x_train)
            y_test_pred = model.predict(x_test)

            train_model_score = r2_score(y_train, y_train_pred)
            test_model_score = r2_score(y_test, y_test_pred)

            report[model_name] = test_model_score

        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys)


def evalute_model(x_train, y_train, x_test, y_test, model=None, param=None, models=None):
    """
    Backward-compatible alias for evaluate_models.
    Supports passing models via either 'model' or 'models' argument.
    """
    if models is None:
        models = model
    return evaluate_models(
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
        models=models,
        param=param,
    )

        