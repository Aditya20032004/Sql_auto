from datasets import Dataset
from transformers import AutoTokenizer
import json
from src.core.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

class SQLDatasetBuilder:
    def __init__(self, tokenizer_name ="google/flan-t5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.examples = []
        
        logger.info(f"Tokenizer loaded: {tokenizer_name}")
        
    def create_training_example(self):
        self.examples =[
            # Basic SELECT queries
            {
                "input": "Get all users",
                "output": "SELECT * FROM users"
            },
            {
                "input": "Show all products",
                "output": "SELECT * FROM products"
            },
            {
                "input": "List all orders",
                "output": "SELECT * FROM orders"
            },
            {
                "input": "Get all customers",
                "output": "SELECT * FROM customers"
            },
            {
                "input": "Show all employees",
                "output": "SELECT * FROM employees"
            },
            
            # WHERE clauses - equality
            {
                "input": "Find active orders",
                "output": "SELECT * FROM orders WHERE status = 'active'"
            },
            {
                "input": "Get pending orders",
                "output": "SELECT * FROM orders WHERE status = 'pending'"
            },
            {
                "input": "Show products in Electronics category",
                "output": "SELECT * FROM products WHERE category = 'Electronics'"
            },
            {
                "input": "Find users from New York",
                "output": "SELECT * FROM users WHERE city = 'New York'"
            },
            
            # WHERE clauses - comparisons
            {
                "input": "Get users with age greater than 25",
                "output": "SELECT * FROM users WHERE age > 25"
            },
            {
                "input": "Show products with price less than 100",
                "output": "SELECT * FROM products WHERE price < 100"
            },
            {
                "input": "Find orders with amount greater than 500",
                "output": "SELECT * FROM orders WHERE amount > 500"
            },
            {
                "input": "Get employees with salary less than 50000",
                "output": "SELECT * FROM employees WHERE salary < 50000"
            },
            {
                "input": "Show products with stock greater than or equal to 10",
                "output": "SELECT * FROM products WHERE stock >= 10"
            },
            
            # COUNT queries
            {
                "input": "Count total products",
                "output": "SELECT COUNT(*) FROM products"
            },
            {
                "input": "Count active users",
                "output": "SELECT COUNT(*) FROM users WHERE active = true"
            },
            {
                "input": "Count orders from today",
                "output": "SELECT COUNT(*) FROM orders WHERE date = CURRENT_DATE"
            },
            {
                "input": "Count customers in California",
                "output": "SELECT COUNT(*) FROM customers WHERE state = 'California'"
            },
            
            # SUM and AVG queries
            {
                "input": "Calculate total sales",
                "output": "SELECT SUM(amount) FROM orders"
            },
            {
                "input": "Get average product price",
                "output": "SELECT AVG(price) FROM products"
            },
            {
                "input": "Calculate average employee salary",
                "output": "SELECT AVG(salary) FROM employees"
            },
            {
                "input": "Sum all order amounts",
                "output": "SELECT SUM(amount) FROM orders"
            },
            
            # JOIN queries
            {
                "input": "Get orders with customer names",
                "output": "SELECT orders.*, customers.name FROM orders JOIN customers ON orders.customer_id = customers.id"
            },
            {
                "input": "Show products with category names",
                "output": "SELECT products.*, categories.name FROM products JOIN categories ON products.category_id = categories.id"
            },
            {
                "input": "List all customers with their orders",
                "output": "SELECT customers.name, orders.* FROM customers JOIN orders ON customers.id = orders.customer_id"
            },
            {
                "input": "Get employees with their department names",
                "output": "SELECT employees.*, departments.name FROM employees JOIN departments ON employees.department_id = departments.id"
            },
            {
                "input": "Show orders with product details",
                "output": "SELECT orders.*, products.name FROM orders JOIN products ON orders.product_id = products.id"
            },
            
            # ORDER BY queries
            {
                "input": "List products ordered by price",
                "output": "SELECT * FROM products ORDER BY price"
            },
            {
                "input": "Show users sorted by name",
                "output": "SELECT * FROM users ORDER BY name"
            },
            {
                "input": "Get orders sorted by date descending",
                "output": "SELECT * FROM orders ORDER BY date DESC"
            },
            {
                "input": "List employees by salary highest first",
                "output": "SELECT * FROM employees ORDER BY salary DESC"
            },
            
            # LIMIT queries
            {
                "input": "Get top 5 products",
                "output": "SELECT * FROM products LIMIT 5"
            },
            {
                "input": "Show first 10 users",
                "output": "SELECT * FROM users LIMIT 10"
            },
            {
                "input": "List 3 most recent orders",
                "output": "SELECT * FROM orders ORDER BY date DESC LIMIT 3"
            },
            
            # GROUP BY queries
            {
                "input": "Count orders by status",
                "output": "SELECT status, COUNT(*) FROM orders GROUP BY status"
            },
            {
                "input": "Get total sales by product",
                "output": "SELECT product_id, SUM(amount) FROM orders GROUP BY product_id"
            },
            {
                "input": "Count users by city",
                "output": "SELECT city, COUNT(*) FROM users GROUP BY city"
            },
            
            # Combined queries
            {
                "input": "Get top 5 expensive products",
                "output": "SELECT * FROM products ORDER BY price DESC LIMIT 5"
            },
            {
                "input": "Find active users older than 30",
                "output": "SELECT * FROM users WHERE active = true AND age > 30"
            },
            {
                "input": "Count pending orders with amount over 100",
                "output": "SELECT COUNT(*) FROM orders WHERE status = 'pending' AND amount > 100"
            },
            {
                "input": "Get average price of Electronics products",
                "output": "SELECT AVG(price) FROM products WHERE category = 'Electronics'"
            },
        ]
        logger.info(f"Created {len(self.examples)} training examples")
        return self.examples

    def prepare_dataset(self):
        model_inputs = self.tokenizer(
            [ex["input"] for ex in self.examples], # inputs
            max_length=128,
            truncation=True,
            padding="max_length",
        )
        # retunr a dictionary with (input_ids, attention_mask)
        labels = self.tokenizer(
            [ex["output"] for ex in self.examples], # outputs
            max_length=128,
            truncation=True,
            padding="max_length",
        )
        tf_list = []
        for label_id in labels["input_ids"]:
            tf_list.append([-100 if id == self.tokenizer.pad_token_id else id for id in label_id])
        
        dataset=Dataset.from_dict({
            "input_ids": model_inputs["input_ids"],
            "attention_mask": model_inputs["attention_mask"],
            "labels": tf_list,
        })
        
        logger.info(f"Dataset prepared with {len(dataset)} examples")
        return dataset
        
    def save_dataset(self, output_path="data/processed/sql_dataset"):
        dataset = self.prepare_dataset()
        dataset.save_to_disk(output_path)
        json_path = output_path + ".json"
        with open(json_path,'w') as f:
            json.dump(self.examples,f,indent =2)
        return dataset
    
    def spider_dataset(self,json_path="data/processed/spider_extracted_dataset.json",max_examples=None):
        logger.info("Loading data from spider json ")
        with open(json_path,'r') as f:
            self.examples = json.load(f)
        
        if max_examples:
            self.examples= self.examples[:max_examples]
        logger.info(f"Loaded max examples:{len(self.examples)}")
        
    
    
    
if __name__ == "__main__":
    logger.info("Starting dataset builder...")
    builder = SQLDatasetBuilder()
    
    builder.create_training_example()
    dataset = builder.prepare_dataset()
    logger.info(f"Dataset ready with {len(dataset)} examples")
    
    