import pandas as pd
import numpy as np
from src.custom_exception import CustomException
from src.logger import get_logger
from config.paths_config import *
from utils.common_functions import read_yaml,load_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

logger=get_logger(__name__)

class DataProcessor:
    def __init__(self,train_path,test_path,processed_dir,config_path):
        self.train_path=train_path
        self.test_path=test_path
        self.processed_dir=processed_dir
        self.config=read_yaml(config_path)
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
    
    def preprocessing(self,df):
        try:
            logger.info("Starting the data preprocessing")
            logger.info("Dropping the unneccessary columns")
            df.drop(columns=['Unnamed: 0', 'Booking_ID'],inplace=True)
            df.drop_duplicates(inplace=True)
            cat_cols=self.config['data_processing']['categorical_columns']
            num_cols=self.config['data_processing']['numerical_columns']
            
            logger.info("Applying Label Encoding")
            
            label_encoder = LabelEncoder()
            mappings={}
            for col in cat_cols:
                df[col] = label_encoder.fit_transform(df[col])
                mappings[col] = {label:code for label,code in zip(label_encoder.classes_ , label_encoder.transform(label_encoder.classes_))}
            
            logger.info(f"Label Mapping :")
            for col,mapping in mappings.items():
                logger.info(f"{col}:{mappings}")
            
            logger.info("Checking multicollinearity")
            X = add_constant(df)

            vif_data = pd.DataFrame()

            vif_data["feature"] = X.columns
            vif_data["VIF"] = [variance_inflation_factor(X.values,i) for i in range(X.shape[1])]
            selected_features = vif_data[vif_data['VIF'] < 5]['feature'].tolist()
            df = df[selected_features]
            logger.info("Performing Skewness Handling")
            skew_threshold=self.config['data_processing']['skewness_threshold']
            skewness=df[num_cols].apply(lambda x:x.skew())
            for column in skewness[skewness>skew_threshold].index:
                df[column]=np.log1p(df[column])
            
            return df
        except Exception as e:
            logger.error(f"Error during preprocessing {e}")
            raise CustomException("Error while preprocessing data", e)
    def balance_data(self,df):
        try:        
            logger.info("Class Imbalance")
            X = df.drop(columns='booking_status')
            y = df["booking_status"]
            smote = SMOTE(random_state=42)
            X_sampled , y_sampled = smote.fit_resample(X,y)
            balanced_df = pd.DataFrame(X_sampled , columns=X.columns)
            balanced_df["booking_status"] = y_sampled
            
            logger.info(" Data Balanced Successfully")
            return balanced_df
        except Exception as e:
            logger.error(f"Error in performing Class Imbalance {e}")
            raise CustomException("Error while balancing data",e)
    def feature_selection(self,df):
        try:
            model =  RandomForestClassifier(random_state=42)
            X = df.drop(columns='booking_status')
            y = df["booking_status"]
            model.fit(X,y)
            feature_importance = model.feature_importances_
            feature_importance_df = pd.DataFrame({'feature':X.columns,'importance':feature_importance})
            top_features_importance_df = feature_importance_df.sort_values(by="importance" , ascending=False)
            num_of_features=self.config['data_processing']['number_of_features']
            top_10_features = top_features_importance_df["feature"].head(num_of_features).values
            logger.info(f"Feature_selected:{top_10_features}")
            top_10_df = df[top_10_features.tolist() + ["booking_status"]]
            logger.info("Feature Selection sucessfully completed")
            return top_10_df
        except Exception as e:
            logger.error(f"Error in feature selection {e}")
            raise CustomException("Error while running the feature selection", e)
    def save_data(self,df,filepath):
        try:
            logger.info("Saving the processed data in the processed folder")
            df.to_csv(filepath,index=False)
            logger.info("Preprocessed data is now saved in the preprocesed folder")
        except Exception as e:
            logger.error(f"Error while saving the file{e}")
            raise CustomException("File was not saved to preprocessed folder", e)
    def preprocess(self):
        try:
            logger.info("Loading data from RAW directory")
            train_df=load_data(self.train_path)
            test_df=load_data(self.test_path)
            train_df=self.preprocessing(train_df)
            test_df=self.preprocessing(test_df)
            train_df=self.balance_data(train_df)
            test_df=self.balance_data(test_df)
            train_df=self.feature_selection(train_df)
            test_df=test_df[train_df.columns]
            self.save_data(train_df,PROCESSED_TRAIN_FILE_PATH)
            self.save_data(test_df,PROCESSED_TEST_FILE_PATH)
            logger.info("Data Processing is sucessfully completed")
        except Exception as e:
            logger.error(f"Error in the processing step{e}")
            raise CustomException("Error in the preprocessing",e)
if __name__=='__main__':
    data_preprocessed=DataProcessor(TRAIN_FILE_PATH,TEST_FILE_PATH,PROCESSED_DIR,CONFIG_PATH)
    data_preprocessed.preprocess()