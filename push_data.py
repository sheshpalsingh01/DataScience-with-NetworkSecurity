import os
import sys
import json
import certifi
import pandas as pd 
import numpy as np 
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logger
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGODB_URI")

ca = certifi.where() # to get the path to the CA bundle, CA mean Certificate authourity



class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def cv_to_json_convertor(self,file_path:str):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records =list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self,records:list,database_name:str,collection_name:str):
        try:
            self.database = database_name
            self.collection = collection_name
            self.records = records
            self.mongo_client =pymongo.MongoClient(MONGO_DB_URL,tlsCAFile=ca)
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)

            return (len(self.records))
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
if __name__ == "__main__":
    file_path = "./Network_Data/phisingData.csv"
    DATABASE ="sheshpalsingh"
    COLLECTION_NAME = "phisingData"  
    obj = NetworkDataExtract()
    records = obj.cv_to_json_convertor(file_path=file_path)
    print("records are ",len(records))
    no_of_records = obj.insert_data_mongodb(records,DATABASE,COLLECTION_NAME)
    print(f"Number of records inserted: {no_of_records}")