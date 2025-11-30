import gradio as gr
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.model_loader import CodeGenerationModel
from src.core.logger import setup_logger

logger = setup_logger(__name__)

# Load the trained model
logger.info("Loading trained SQL model...")
model = CodeGenerationModel(model_name_or_path="models/trained_sql_model")
logger.info("Model loaded successfully!")

def generate_sql(prompt):
    """
    Generate SQL query from natural language prompt
    """
    try:
        logger.info(f"Generating SQL for: {prompt}")
        sql_query = model.generate(prompt=prompt, max_length=100)
        logger.info(f"Generated: {sql_query}")
        return sql_query
    except Exception as e:
        logger.error(f"Error generating SQL: {e}")
        return f"Error: {str(e)}"

# Example prompts
examples = [
    ["Get all users"],
    ["Show all products"],
    ["Count total orders"],
    ["What is the average price of products"],
    ["List employees ordered by salary"],
    ["Get top 5 products"],
    ["Find active orders"],
    ["Show customers with their orders"],
    ["What are the names of employees who earn more than the average salary"],
]

# Create Gradio interface
with gr.Blocks(title="Text-to-SQL Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🔍 Text-to-SQL Generator
        
        Transform natural language queries into SQL using a fine-tuned FLAN-T5 model.
        
        **Model Details:**
        - Base Model: google/flan-t5-base (250M parameters)
        - Training Dataset: Spider benchmark (8,000 examples)
        - Accuracy: 71.7% semantic similarity, 91.8% keyword match
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            input_text = gr.Textbox(
                label="Natural Language Query",
                placeholder="Enter your question in plain English...",
                lines=3
            )
            
            generate_btn = gr.Button("Generate SQL", variant="primary", size="lg")
            
            output_text = gr.Textbox(
                label="Generated SQL Query",
                lines=5,
                interactive=False
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 💡 Example Queries")
            gr.Examples(
                examples=examples,
                inputs=input_text,
                label="Click to try:",
            )
    
    gr.Markdown(
        """
        ---
        ### 📊 Project Highlights
        - **Fine-tuned** on 8,000 Spider dataset examples (research-grade benchmark)
        - **Encoder-Decoder** transformer architecture (T5)
        - **GPU-optimized** training pipeline with TensorFlow
        - **Production-ready** MLOps implementation
        """
    )
    
    # Connect the button to the function
    generate_btn.click(
        fn=generate_sql,
        inputs=input_text,
        outputs=output_text
    )
    
    # Also trigger on Enter key
    input_text.submit(
        fn=generate_sql,
        inputs=input_text,
        outputs=output_text
    )

if __name__ == "__main__":
    logger.info("Starting Gradio app...")
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=True  # Set to True for public link
    )
