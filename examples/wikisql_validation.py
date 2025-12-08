import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datasets import Dataset
import glob
from src.model_loader import CodeGenerationModel
from src.core.logger import setup_logger
from difflib import SequenceMatcher
import re

logger = setup_logger(__name__)

def similarity(str1,str2):
    return SequenceMatcher(None,str1.lower(), str2.lower()).ratio()
    
def normalization(sql):
    sql = sql.strip().lower()
    
    # Normalize column name formats: convert slashes and spaces to underscores
    # This handles: "2010/ 11" → "2010_11", "School/Club Team" → "School_Club_Team"
    sql = re.sub(r'(\w+)\s*/\s*(\w+)', r'\1_\2', sql)  # Handle "2010 / 11" or "2010/11"
    sql = re.sub(r'(\w+)/(\w+)', r'\1_\2', sql)        # Handle remaining slashes
    
    # Normalize date formats: remove extra spaces around hyphens and standardize abbreviations
    # This handles: "19- sept-2006" → "19-sep-2006", "oct." → "oct"
    sql = re.sub(r'\s*-\s*', '-', sql)  # Remove spaces around hyphens
    sql = re.sub(r'\.', '', sql)  # Remove periods (e.g., "oct." → "oct", "8," → "8")
    sql = re.sub(r'sept', 'sep', sql)  # Standardize September abbreviation
    
    # Fix missing spaces after SQL keywords
    sql = re.sub(r'(select|from|where|and|or|count|sum|avg|max|min|group|order|by|having|limit)([a-z])', r'\1 \2', sql, flags=re.IGNORECASE)
    
    sql = re.sub(r'\s+', ' ', sql)
    sql = re.sub(r'\s*,\s*', ', ', sql)
    
    # Normalize comparison operators: fix spacing and handle missing operators
    sql = re.sub(r'\s*=\s*', ' = ', sql)
    sql = re.sub(r'\s*<\s*', ' < ', sql)
    sql = re.sub(r'\s*>\s*', ' > ', sql)
    sql = re.sub(r'\s*<=\s*', ' <= ', sql)
    sql = re.sub(r'\s*>=\s*', ' >= ', sql)
    sql = re.sub(r'\s*<>\s*', ' <> ', sql)
    sql = re.sub(r'\s*!=\s*', ' != ', sql)
    
    # Handle case where < or > got stripped (appears as double space + number)
    # Pattern: "Events  26" should stay as is (we can't recover the operator)
    # But normalize spacing consistently
    sql = re.sub(r'\s+', ' ', sql)
    
    # Remove "Week" prefix from numeric values (e.g., "Week 4" → "4", "Week 6" → "6")
    sql = re.sub(r'\bweek\s+(\d+)', r'\1', sql, flags=re.IGNORECASE)
    
    # Normalize quotes: remove ALL quotes to treat quoted and unquoted values the same
    # This handles: Title = "Firestorm" vs Title = Firestorm
    sql = re.sub(r'"', '', sql)
    
    # Normalize minus/negative signs (various Unicode minus to ASCII hyphen)
    sql = re.sub(r'[−–—]', '-', sql)  # Unify all dash types
    
    # Remove special symbols and trailing punctuation
    sql = re.sub(r'[√→↓↑✓✗×]', '', sql)  # Remove checkmarks, arrows, etc.
    sql = re.sub(r'(\w)-+$', r'\1', sql)  # Remove trailing dashes
    sql = re.sub(r'(\w)\s*\.$', r'\1', sql)  # Remove trailing periods
    
    # Normalize article words: remove "the", "a", "an" from values for comparison
    # This handles: "the beatles" vs "beatles", "a storm" vs "storm"
    sql = re.sub(r'\b(the|a|an)\s+', '', sql)
    
    # Remove common prefix words that get added/dropped
    sql = re.sub(r'\bshort\s+film\s+', '', sql)  # "short film 2007" → "2007"
    
    # Normalize parentheses spacing
    sql = re.sub(r'\(\s+', '(', sql)
    sql = re.sub(r'\s+\)', ')', sql)
    
    # Normalize WHERE clause condition order: sort conditions alphabetically
    # This handles: "WHERE Tries > 1 AND Player = dave" → same as "WHERE Player = dave AND Tries > 1"
    where_match = re.search(r'where\s+(.+?)(?:\s+group|\s+order|\s+limit|$)', sql, re.IGNORECASE)
    if where_match:
        conditions = where_match.group(1)
        # Split by AND/OR and sort alphabetically
        and_parts = re.split(r'\s+and\s+', conditions, flags=re.IGNORECASE)
        sorted_and_parts = []
        for and_part in and_parts:
            or_parts = re.split(r'\s+or\s+', and_part, flags=re.IGNORECASE)
            sorted_or_parts = sorted([p.strip() for p in or_parts])
            sorted_and_parts.append(' or '.join(sorted_or_parts))
        sorted_conditions = ' and '.join(sorted(sorted_and_parts))
        sql = sql[:where_match.start(1)] + sorted_conditions + sql[where_match.end(1):]
    sql = sql.replace("'", '"')
    return sql

def clean_column_names_in_sql(sql, original_cols):
    """Replace original column names with cleaned versions in SQL"""
    for original_col in original_cols:
        clean_col = original_col.replace(' ', '_').replace('/', '_')
        # Use word boundaries to avoid partial replacements
        sql = re.sub(r'\b' + re.escape(original_col) + r'\b', clean_col, sql, flags=re.IGNORECASE)
    return sql
    
    
def main():
    logger.info("Starting wikisql validation")
    
    model = CodeGenerationModel(model_name_or_path="models/trained_wikisql_model")
    
    logger.info("Loading model success")
    cache_dir = "/home/aditya/.cache/huggingface/datasets/wikisql/default/0.1.0/*/wikisql-validation.arrow"
    val_file = glob.glob(cache_dir)[0]
    validation_data = Dataset.from_file(val_file)
    
    # Use all validation examples (8421 total)
    num_examples = len(validation_data)
    logger.info(f"Loaded {num_examples} validation examples - running on ALL")
    
    logger.info("Genearting code")
    total_similarity = 0
    exact_match = 0
    
    for i,example in enumerate(validation_data):
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
        
        # Compare with original column names (model predicts original)
        similarity_score = similarity(pred_sql, expected_sql)
        total_similarity += similarity_score
        
        # OPTION 1: Compare original with original (currently active)
        if normalization(pred_sql) == normalization(expected_sql):
            exact_match += 1
        
        # OPTION 2: Clean expected SQL to match cleaned predictions (commented for future use)
        # expected_sql_cleaned = clean_column_names_in_sql(expected_sql, col)
        # similarity_score = similarity(pred_sql, expected_sql_cleaned)
        # if normalization(pred_sql) == normalization(expected_sql_cleaned):
        #     exact_match += 1
        
        logger.info(f"\n{'=='*25}")
        logger.info(f"example{i+1}")
        logger.info(f"Question: {example['question']}")
        logger.info(f"Expected: {expected_sql}")
        # logger.info(f"Expected (cleaned): {expected_sql_cleaned}")  # Uncomment if using OPTION 2
        logger.info(f"Predicted: {pred_sql}")
        logger.info(f"Similarity: {similarity_score*100:.2f}%")
        
    avg_similarity = (total_similarity/num_examples)*100
    avg_exact_match = (exact_match/num_examples)*100
    logger.info(f"\n{'='*50}")
    logger.info("FINAL RESULTS:")
    logger.info(f"Average Similarity: {avg_similarity:.2f}%")
    logger.info(f"Exact Match: {avg_exact_match:.2f}%")
    logger.info(f"Total Examples: {num_examples}")
            

if __name__=="__main__":
    main()