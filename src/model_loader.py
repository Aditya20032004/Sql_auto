import tensorflow as tf
from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer
from src.core.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

class CodeGenerationModel:
    def __init__(self, model_name_or_path: str="google/flan-t5-base"):
        logger.info(f"Loading model: {model_name_or_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = TFAutoModelForSeq2SeqLM.from_pretrained(model_name_or_path,
                                                            trust_remote_code=True,)
        logger.info("Model and tokenizer loaded successfully")
    
    def generate(self, prompt: str, max_length: int=50):
        logger.info(f"Generating code for prompt: {prompt}")
        inputs = self.tokenizer(
            prompt, return_tensors="tf",
            max_length=128,
            truncation=True,
        )
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,temperature=0.3,            
        )
        code = self.tokenizer.decode(outputs[0],skip_special_tokens=True)
        logger.info(f"Generated code: {code}")
        return code

if __name__ == "__main__":
    logger.info("Starting code generation test")
    model = CodeGenerationModel()
    prompts = [
    "Generate SQL query: SELECT all columns from users table",
    "Generate SQL query: Find orders where status equals 'active'",
    "Generate SQL query: Count rows in products table"
    ]
    for prompt in prompts:
        print("-"*25)
        model.generate(prompt)
    print("Done")