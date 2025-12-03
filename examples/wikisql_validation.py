import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datasets import Dataset
import glob
from src.model_loader import CodeGenerationModel
from src.core.logger import setup_logger
from difflib import SequenceMatcher

logger = setup_logger(__name__)

def similarity(str1,str2):
    return SequenceMatcher(None,str1.lower(), str2.lower()).ratio()
    
    
    
def main():
    logger.info("Starting wikisql validation")
    
    model = CodeGenerationModel(model_name_or_path="models/trained_wikisql_model")
    
    logger.info("LOading model success")
    cache_dir = "/home/aditya/.cache/huggingface/datasets/wikisql/default/0.1.0/*/wikisql-validation.arrow"
    val_file = glob.glob(cache_dir)[0]
    val_file = Dataset.from_file(val_file)
    num_examples=15
    val_file = val_file.select(range(num_examples))
    logger.info(f"loaded{num_examples} successfully")
    
    logger.info("Genearting code")
    total_similarity = 0
    exact_match = 0
    
    for i,example in enumerate(val_file):
        tn = example['table']['name']
        col = example['table']['header']
        types = example['table']['types']
        
        col_defs = []
        for c,t in zip(col,types):
            clean_col = c.replace(' ','_').replace('/','_')
            sql_type = 'REAL' if t=='real' else 'TEXT'
            col_defs.append(f"{clean_col} {sql_type}")
        create_sql_stat = f"CREATE TABLE {tn} {(', '.join(col_defs))}"
        input_text = f"{create_sql_stat});Question: {example['question']}"
        
        pred_sql = model.generate(prompt=input_text,max_length=128)
        expected_sql = example['sql']['human_readable']
        similarity_score = similarity(pred_sql,expected_sql)
        total_similarity +=similarity_score
        
        if pred_sql.strip().lower()==expected_sql.strip().lower():
            exact_match+=1
        if i<5:
            logger.info(f"\n{'=='*25}")
            logger.info(f"example{i+1}")
            logger.info(f"Question: {example['question']}")
            logger.info(f"Expected: {expected_sql}")
            logger.info(f"Predicted: {pred_sql}")
            logger.info(f"Similarity: {similarity_score*100:2f}%")
        
    avg_similarity = (total_similarity/num_examples)*100
    avg_exact_match = (exact_match/num_examples)*100
    logger.info(f"\n{'='*50}")
    logger.info("FINAL RESULTS:")
    logger.info(f"Average Similarity: {avg_similarity:.2f}%")
    logger.info(f"Exact Match: {avg_exact_match:.2f}%")
    logger.info(f"Total Examples: {num_examples}")
            

if __name__=="__main__":
    main()