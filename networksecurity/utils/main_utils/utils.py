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
        with open(file_path,'rb') as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys)
        