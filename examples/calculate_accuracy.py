import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model_loader import CodeGenerationModel
from difflib import SequenceMatcher

def calculate_similarity(str1, str2):
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() * 100

def main():
    model = CodeGenerationModel(model_name_or_path="models/trained_sql_model")
    
    test_cases = [
        ("Get all records from users table", "SELECT * FROM users"),
        ("Show all records from products table", "SELECT * FROM products"),
        ("Find orders from orders table where status is active", "SELECT * FROM orders WHERE status = 'active'"),
        ("Get records from users table where age is greater than 25", "SELECT * FROM users WHERE age > 25"),
        ("Count total records in products table", "SELECT COUNT(*) FROM products"),
        ("What is the average price from products table", "SELECT AVG(price) FROM products"),
        ("What are the maximum and minimum salaries from employees table", "SELECT MAX(salary), MIN(salary) FROM employees"),
        ("List all records from employees table ordered by salary", "SELECT * FROM employees ORDER BY salary"),
        ("Show all records from products table sorted by price descending", "SELECT * FROM products ORDER BY price DESC"),
        ("Get top 5 records from products table", "SELECT * FROM products LIMIT 5"),
        ("Show first 10 records from customers table", "SELECT * FROM customers LIMIT 10"),
        ("List all customers from customers table with their orders from orders table joining on customers.id = orders.customer_id", "SELECT * FROM customers JOIN orders ON customers.id = orders.customer_id"),
        ("Get orders with customer names by joining orders and customers tables on orders.customer_id = customers.id", "SELECT orders.*, customers.name FROM orders JOIN customers ON orders.customer_id = customers.id"),
        ("Count orders by status from orders table grouped by status", "SELECT status, COUNT(*) FROM orders GROUP BY status"),
        ("Get total sales amount by product_id from sales table grouped by product_id", "SELECT product_id, SUM(amount) FROM sales GROUP BY product_id"),
    ]
    
    exact_matches = 0
    total_similarity = 0
    
    print("\n" + "="*100)
    print("ACCURACY EVALUATION")
    print("="*100 + "\n")
    
    for i, (prompt, expected) in enumerate(test_cases, 1):
        generated = model.generate(prompt=prompt, max_length=100)
        
        similarity = calculate_similarity(expected, generated)
        total_similarity += similarity
        
        is_exact = expected.lower().strip() == generated.lower().strip()
        if is_exact:
            exact_matches += 1
        
        print(f"Test {i}:")
        print(f"  Prompt:    {prompt}")
        print(f"  Expected:  {expected}")
        print(f"  Generated: {generated}")
        print(f"  Similarity: {similarity:.2f}%")
        print(f"  Exact Match: {'✓' if is_exact else '✗'}")
        print("-" * 100)
    
    exact_accuracy = (exact_matches / len(test_cases)) * 100
    avg_similarity = total_similarity / len(test_cases)
    
    print("\n" + "="*100)
    print("FINAL RESULTS")
    print("="*100)
    print(f"Total Test Cases: {len(test_cases)}")
    print(f"Exact Matches: {exact_matches}/{len(test_cases)}")
    print(f"Exact Match Accuracy: {exact_accuracy:.2f}%")
    print(f"Average Similarity: {avg_similarity:.2f}%")
    print("="*100 + "\n")

if __name__ == "__main__":
    main()
