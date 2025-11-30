import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model_loader import CodeGenerationModel
from src.core.logger import setup_logger

logger= setup_logger(__name__)

def main():
    logger.info("Testing started for trained model...")
    
    model = CodeGenerationModel(model_name_or_path="models/trained_sql_model")
    test_prompts= [
        # Basic SELECT
        "Get all users",
        "Show all products",
        
        # WHERE clauses
        "Find active orders",
        "Get users with age greater than 25",
        
        # Aggregations
        "Count total products",
        "What is the average price of products",
        "What are the maximum and minimum salaries",
        
        # ORDER BY
        "List employees ordered by salary",
        "Show products sorted by price descending",
        
        # LIMIT
        "Get top 5 products",
        "Show first 10 customers",
        
        # JOIN
        "List all customers with their orders",
        "Get orders with customer names",
        "Show products with category information",
        
        # GROUP BY
        "Count orders by status",
        "Get total sales by product",
        
        # Complex queries
        "How many departments have more than 10 employees",
        "List the names of students who registered for statistics course",
        "What are the names of employees who earn more than the average salary",
    ]
    
    logger.info("Now generating SQL queries for test prompts...")
    for prompt in test_prompts:
        logger.info("-"*25)
        logger.info(f"prompt given:{prompt}")
        
        sql = model.generate(prompt=prompt, max_length=100)
        logger.info(f"Generated SQL: {sql}")
        print()
    
    logger.info("Testing completed.")

if __name__ == "__main__":
    main()
        
    