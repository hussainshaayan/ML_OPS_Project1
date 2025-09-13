import os
import pandas as pd
from src.logger import get_logger
from src.custom_exception import CustomException
import yaml

logger=get_logger(__name__)

def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File is not in the file path")
        
        with open(file_path,"r") as yaml_path:
            config=yaml.safe_load(yaml_path)
            logger.info("Successfully read the YAML File")
            return config
        
    except Exception as e:
        logger.error("Error while reading the YAML file")
        raise CustomException("Failed to read Customer YAML file", e)
    
def load_data(path):
    try:
        logger.info("Loading the data")
        return pd.read_csv(path)
    except Exception as e:
        logger.error(f"Error while loading the data{path}")
        raise CustomException("Not able to load the file", e)