import os
import pandas as pd
import joblib 
from sklearn.model_selection import RandomizedSearchCV
import lightgbm as lgb
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score
from src.custom_exception import CustomException
from src.logger import get_logger
from config.paths_config import *
from config.model_params import *
from scipy.stats import randint
from utils.common_functions import read_yaml,load_data
import mlflow
import mlflow.sklearn

logger=get_logger(__name__)

class ModelTraining:
    def __init__(self,train_path,test_path,model_output_path):
        self.train_path=train_path
        self.test_path=test_path
        self.model_output_path=model_output_path
        
        self.params_dist=LIGHTGM_PARAMS
        self.random_search_params=RANDOM_SEARCH_PARAMS
        
        
    def load_and_split_data(self):
        try:
            logger.info(f"Loading the from {self.train_path}")
            train_df=load_data(self.train_path)
            
            logger.info(f"Load data from {self.test_path}")
            test_df=load_data(self.test_path)
            
            x_train = train_df.drop(columns='booking_status')
            y_train = train_df["booking_status"]
            x_test = test_df.drop(columns='booking_status')
            y_test = test_df["booking_status"]
            
            logger.info(" Data splitted successfully for Model Training")
            
            return x_train,y_train,x_test,y_test
        except Exception as e:
            logger.info(f"Error loading while loading data{e}")
            raise CustomException("Data splitting successfully for Model Training",e)
    def train_lgm(self,x_train,y_train):
        try:
            logger.info("Intializing our model")
            
            lgbm_model=lgb.LGBMClassifier(random_state=self.random_search_params['random_state'])
            
            logger.info("Starting our Hyperparameter tuning")
            
            random_search=RandomizedSearchCV(estimator=lgbm_model,param_distributions=self.params_dist,n_iter = self.random_search_params["n_iter"],
                cv = self.random_search_params["cv"],
                n_jobs=self.random_search_params["n_jobs"],
                verbose=self.random_search_params["verbose"],
                random_state=self.random_search_params["random_state"],
                scoring=self.random_search_params["scoring"])
            
            logger.info("Starting our model training")
            random_search.fit(x_train,y_train)
            logger.info("Hyper Parameter tuning completed")
            best_params=random_search.best_params_
            best_lgm_model=random_search.best_estimator_
            
            logger.info(f"Best Parameter : {best_params}")
            
            return best_lgm_model
        except Exception as e:
            logger.error(f"Erro was found in the {e}")
            raise CustomException("Training couldn't complete",e)
    def evaluate_model(self,model,x_test,y_test):
        try:
            logger.info("Checking the model performance")
            y_pred=model.predict(x_test)
            accuracy = accuracy_score(y_test,y_pred)
            precision = precision_score(y_test,y_pred)
            recall = recall_score(y_test,y_pred)
            f1 = f1_score(y_test,y_pred)
            logger.info(f"Accuracy of the model:{accuracy}")
            logger.info(f"Recall of the model:{recall}")
            logger.info(f"Precision of the model:{precision}")
            logger.info(f"f1 score of the model:{f1}")
            return {'Accuracy':accuracy,"Recall":recall,"Precision":precision,"F1 score":f1}
        except Exception as e:
            logger.error("Error was found during evaluation{e}")
            raise CustomException("Model Evaluation was unsuccessful",e)
    def save_model(self,model):
        try:
            os.makedirs(os.path.dirname(self.model_output_path),exist_ok=True)
            joblib.dump(model,self.model_output_path)
            logger.info(f"Model is successfully Uploaded{self.model_output_path}")
        except Exception as e:
            logger.error("Error was found while saving model{e}")
            raise CustomException("Model save was unsuccessful",e)
    def run(self):
        try:
            with mlflow.start_run():
                logger.info("Starting our model training pipeline")
                logger.info("Starting our ml flow experimentation")
                
                logger.info("Logging the training and testing dataset")
                mlflow.log_artifact(self.train_path,artifact_path="datasets")
                mlflow.log_artifact(self.test_path,artifact_path="datasets")
                x_train,y_train,x_test,y_test=self.load_and_split_data()
                best_lgm_model=self.train_lgm(x_train,y_train)
                metrics=self.evaluate_model(best_lgm_model,x_test,y_test)
                self.save_model(best_lgm_model)
                logger.info("Logging the Model in MLFLOW")
                mlflow.log_artifact(self.model_output_path)
                mlflow.log_params(best_lgm_model.get_params())
                mlflow.log_metrics(metrics)
                logger.info("Model Pipeline ran successfully ")
        except Exception as e:
            logger.error("Error was found while running the model pipeline{e}")
            raise CustomException("Model pipelne ran was unsuccessfully",e) 
if __name__=="__main__":
    model_pipeline=ModelTraining(PROCESSED_TRAIN_FILE_PATH,PROCESSED_TEST_FILE_PATH,MODEL_OUTPUT_PATH)  
    model_pipeline.run() 
            
            