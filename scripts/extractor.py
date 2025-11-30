import pandas as pd
# df= pd.read_csv("/home/aditya/mlproj/llm_training_ex/data/sql/spider_text_sql.csv")
import json
from src.core.logger import setup_logger
logger = setup_logger(__name__)
 
 
def load_data_spider(csv_path,num_examples= 8000):
     logger.info("LOADING DATA FROM SPIDER CSV")
     df = pd.read_csv(csv_path)
     logger.info(f"Total row:{len(df)}")
     logger.info(f"columns:{len(list(df.columns))}")
     logger.info(f"Columns are:{list(df.columns)}")
     
     df_ex = df.head(num_examples)
     examples = []
     for _,row in df_ex.iterrows():
         examples.append({
             "input":row["text_query"],"output":row["sql_command"]
         })
     logger.info(f"example save success")
     return examples
 
def save_examples(examples,output_path):
    with open(output_path,'w') as f:
        json.dump(examples, f, indent = 2)
    logger.info(f"examples saved at {output_path}")
    
def display_spider_dataset(examples,num_samples=5):
    logger.info("Displaying samples from spider dataset")
    for i,r in enumerate(examples[:num_samples],start=1):
        logger.info(f"sample{i}")
        logger.info(f"In:{r['input']}")
        logger.info(f"In:{r['output']}")
        
if __name__=="__main__":
    csv_path ="/home/aditya/mlproj/llm_training_ex/data/sql/spider_text_sql.csv"
    examples = load_data_spider(csv_path,num_examples=8000)
    save_examples(examples,"/home/aditya/mlproj/llm_training_ex/data/processed/spider_extracted_dataset.json")
    display_spider_dataset(examples,num_samples=5)
    logger.info("Extract completed")