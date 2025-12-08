import gradio as gr
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.model_loader import CodeGenerationModel
from src.core.logger import setup_logger

logger = setup_logger(__name__)

# Load the trained model
logger.info("Loading trained WikiSQL model...")
model = CodeGenerationModel(model_name_or_path="models/trained_wikisql_model")
logger.info("Model loaded successfully!")

def parse_input(user_input):
    """
    Parse user input to extract schema and question
    Supports two formats:
    1. Full format: "CREATE TABLE ... ; Question: ..."
    2. Question only: "What is the ..." (uses default table)
    """
    if "CREATE TABLE" in user_input.upper() and "Question:" in user_input:
        return user_input
    else:
        # Provide a default schema for question-only input
        default_schema = "CREATE TABLE table (column TEXT, value REAL);"
        return f"{default_schema} Question: {user_input}"

def generate_sql(user_input, include_schema=True):
    """
    Generate SQL query from natural language input with schema context
    
    Args:
        user_input: Natural language question or full CREATE TABLE + Question format
        include_schema: Whether to expect schema in input (default: True)
    
    Returns:
        Generated SQL query
    """
    try:
        start_time = time.time()
        logger.info(f"User input: {user_input[:100]}...")
        
        # Parse input to ensure proper format
        formatted_input = parse_input(user_input)
        
        # Generate SQL
        sql_query = model.generate(prompt=formatted_input, max_length=128)
        
        elapsed = time.time() - start_time
        logger.info(f"Generated SQL in {elapsed:.2f}s: {sql_query}")
        
        return sql_query, f"✓ Generated in {elapsed:.2f}s"
    
    except Exception as e:
        logger.error(f"Error generating SQL: {e}")
        return f"Error: {str(e)}", "✗ Generation failed"

# Professional example queries with schema context
examples = [
    ["""CREATE TABLE employees (Name TEXT, Department TEXT, Salary REAL, Years_Experience REAL);
Question: What are the names of employees in the Engineering department?"""],
    
    ["""CREATE TABLE products (Product_Name TEXT, Category TEXT, Price REAL, Stock_Quantity REAL);
Question: Which products cost more than 100 dollars?"""],
    
    ["""CREATE TABLE orders (Order_ID REAL, Customer_Name TEXT, Order_Date TEXT, Total_Amount REAL);
Question: What is the total amount of all orders?"""],
    
    ["""CREATE TABLE students (Student_Name TEXT, Grade TEXT, GPA REAL, Graduation_Year REAL);
Question: How many students have a GPA greater than 3.5?"""],
    
    ["""CREATE TABLE movies (Title TEXT, Director TEXT, Year REAL, Rating REAL, Genre TEXT);
Question: What movies were directed by Christopher Nolan?"""],
    
    ["""CREATE TABLE sales (Region TEXT, Product TEXT, Revenue REAL, Units_Sold REAL);
Question: What is the average revenue per region?"""],
]

# Custom CSS for professional styling
custom_css = """
.gradio-container {
    font-family: 'Inter', sans-serif;
}
.header-text {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 20px;
}
.stats-box {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}
"""

# Create professional Gradio interface
with gr.Blocks(title="WikiSQL Text-to-SQL Generator", theme=gr.themes.Soft(), css=custom_css) as demo:
    
    # Header
    gr.HTML("""
        <div class="header-text">
            <h1>🗄️ WikiSQL Text-to-SQL Generator</h1>
            <p style="font-size: 1.1em; margin-top: 10px;">
                Transform natural language into executable SQL queries using fine-tuned FLAN-T5
            </p>
        </div>
    """)
    
    # Main content
    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("### 📝 Input")
            
            input_text = gr.Textbox(
                label="Schema + Question",
                placeholder="""Enter in format:
CREATE TABLE table_name (column1 TYPE, column2 TYPE, ...);
Question: Your natural language question here

OR just enter a question (default schema will be used)""",
                lines=6,
                info="Provide table schema followed by your question for best results"
            )
            
            with gr.Row():
                generate_btn = gr.Button("🚀 Generate SQL", variant="primary", size="lg", scale=3)
                clear_btn = gr.Button("🗑️ Clear", size="lg", scale=1)
            
            gr.Markdown("### ✨ Generated SQL")
            output_text = gr.Textbox(
                label="SQL Query",
                lines=4,
                interactive=False,
                placeholder="Your SQL query will appear here..."
            )
            
            status_text = gr.Textbox(
                label="Status",
                lines=1,
                interactive=False,
                show_label=False
            )
        
        with gr.Column(scale=2):
            gr.Markdown("### 💡 Example Queries")
            gr.Examples(
                examples=examples,
                inputs=input_text,
                label="Click to try:",
            )
    
    # Model Information Section
    gr.Markdown("---")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("""
            <div class="stats-box">
            
            ### 📊 Model Performance
            - **Semantic Similarity:** 96.14%
            - **Exact Match:** 61.23%
            - **Validation Examples:** 8,421
            - **Training Examples:** 56,355
            
            </div>
            """)
        
        with gr.Column():
            gr.Markdown("""
            <div class="stats-box">
            
            ### 🔧 Technical Details
            - **Base Model:** Google FLAN-T5-base (250M params)
            - **Dataset:** WikiSQL (single-table queries)
            - **Training Loss:** 0.0206 (epoch 18)
            - **Beam Search:** num_beams=5
            
            </div>
            """)
        
        with gr.Column():
            gr.Markdown("""
            <div class="stats-box">
            
            ### 🎯 Key Features
            - Schema-aware SQL generation
            - Beam search decoding (k=5)
            - Gradient clipping (clipnorm=1.0)
            - Early stopping (patience=5)
            
            </div>
            """)
    
    gr.Markdown("""
    ---
    ### 📖 How to Use
    1. **Provide Schema:** Start with `CREATE TABLE` statement defining your table structure
    2. **Ask Question:** Add `Question:` followed by your natural language query
    3. **Generate:** Click the button to get your SQL query
    
    **Note:** This model is trained on WikiSQL (single-table queries). For best results, use simple SELECT statements with WHERE clauses and aggregations.
    
    **Project Repository:** [GitHub](https://github.com/Aditya20032004/Sql_auto) | **Model Highlights:** Discovered WikiSQL preprocessing bug, engineered 7-layer normalization achieving 2.3x accuracy improvement
    """)
    
    # Event handlers
    generate_btn.click(
        fn=generate_sql,
        inputs=input_text,
        outputs=[output_text, status_text]
    )
    
    clear_btn.click(
        fn=lambda: ("", "", ""),
        inputs=None,
        outputs=[input_text, output_text, status_text]
    )
    
    input_text.submit(
        fn=generate_sql,
        inputs=input_text,
        outputs=[output_text, status_text]
    )

if __name__ == "__main__":
    logger.info("Starting Gradio app...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Set to True for public Gradio link
        show_error=True
    )
