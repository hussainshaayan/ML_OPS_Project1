from src.logger import get_logger
from src.custom_exception import CustomException
import sys

logger=get_logger(__name__)

def divide_number(n,s):
    try:
        result=n/s
        logger.info("diving two numbers")
        return result
    except Exception as e:
        logger.error("Error Occured")
        raise CustomException("Den might be zero",sys)
    
if __name__=="__main__":
    try:
        logger.info("Start the program")
        divide_number(10,0)
    except CustomException as ce:
        logger.error(str(ce))