import pandas as pd
import json
import re
from src.core.logger import setup_logger

logger = setup_logger(__name__)

def simplify_query(query):
    """Clean and simplify SQL query"""
    # Remove extra spaces and newlines
    query = re.sub(r'\s+', ' ', query.strip())
    # Remove parameters like p1, p2, etc
    query = re.sub(r'\bp\d+\b', '?', query)
    # Remove collection references
    query = re.sub(r'collection\d+_', '?', query)
    return query

def generate_natural_language(query):
    """Generate simple natural language description from SQL query"""
    query_lower = query.lower()
    
    # Basic patterns
    if 'select max' in query_lower and 'from' in query_lower:
        table = re.search(r'from\s+([\w.]+)', query_lower)
        if table:
            return f"Get maximum value from {table.group(1)}"
    
    if 'select a from' in query_lower and 'left join' in query_lower:
        table = re.search(r'from\s+([\w.]+)', query_lower)
        if table:
            return f"Get records from {table.group(1)} with left join"
    
    if 'select' in query_lower and 'where' in query_lower:
        table = re.search(r'from\s+([\w.]+)', query_lower)
        if table:
            return f"Find records from {table.group(1)} with conditions"
    
    if 'select' in query_lower and 'from' in query_lower:
        table = re.search(r'from\s+([\w.]+)', query_lower)
        if table:
            return f"Get all from {table.group(1)}"
    
    return "Execute SQL query"

def main():
    logger.info("Reading CSV file...")
    
    # Read CSV
    csv_path = "/home/aditya/mlproj/llm_training_ex/data/processed/finalcsv_cutted.csv"
    df = pd.read_csv(csv_path)
    
    logger.info(f"Total rows in CSV: {len(df)}")
    logger.info(f"Columns: {list(df.columns)}")
    
    # Extract unique queries (sample first 1000 for now)
    queries = df['query'].head(1000).unique()
    logger.info(f"Unique queries in first 1000 rows: {len(queries)}")
    
    # Create training examples
    examples = []
    for query in queries[:100]:  # Take first 100 unique queries
        if pd.isna(query) or len(str(query).strip()) == 0:
            continue
            
        clean_query = simplify_query(str(query))
        nl_description = generate_natural_language(clean_query)
        
        examples.append({
            "input": nl_description,
            "output": clean_query
        })
    
    logger.info(f"Created {len(examples)} examples")
    
    # Save to JSON
    output_path = "/home/aditya/mlproj/llm_training_ex/data/processed/csv_extracted_dataset.json"
    with open(output_path, 'w') as f:
        json.dump(examples, f, indent=2)
    
    logger.info(f"Saved examples to {output_path}")
    
    # Show sample
    logger.info("Sample examples:")
    for ex in examples[:5]:
        logger.info(f"Input: {ex['input']}")
        logger.info(f"Output: {ex['output']}")
        logger.info("---")

if __name__ == "__main__":
    main()
