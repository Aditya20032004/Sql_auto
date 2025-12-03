from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer
from datasets import load_from_disk
import tensorflow as tf
from src.core.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

class ModelTrainer:
    def __init__(self, model_name_or_path="google/flan-t5-base", dataset_path=None):
        logger.info(f"Loading model: {model_name_or_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = TFAutoModelForSeq2SeqLM.from_pretrained(model_name_or_path)
        
        if dataset_path:
            logger.info(f"Loading dataset from: {dataset_path}")
            self.dataset = load_from_disk(dataset_path)
        else:
            self.dataset = None
        
        logger.info("Model and tokenizer loaded successfully!")
    
    def train(self, epochs=3,lr = 0.00005,#5e-5
              batch_size=4, callbacks=None):
        if self.dataset is None:
            logger.error("No dataset loaded. Provide dataset_path in __init__")
            return 
        logger.info(f"starting training for {epochs} epochs with lr {lr} and batch size {batch_size}")
        
        optimizer = tf.keras.optimizers.Adam(lr=lr)
        self.model.compile(optimizer=optimizer)
        logger.info("Model compiled successfully")
        
        logger.info("converting data into tf format")
        tf_dataset = self.model.prepare_tf_dataset(
            self.dataset,
            batch_size=batch_size,
            shuffle =True,
            tokenizer=self.tokenizer,
            collate_fn=None, # NEW ADDED
        )
        
        logger.info("Dataset converted to tf and starting training...")
        
        history = self.model.fit(tf_dataset,epochs=epochs,verbose=1, callabacks = callbacks)
        logger.info("Training completed.")
        return history
        
        
    def save_model(self,output_path = "models/trained_sql_model"):        
        self.model.save_pretrained(output_path)
        logger.info(f"starting to save model at {output_path}")
        
        self.tokenizer.save_pretrained(output_path)
        logger.info(f"starting to save tokenizer at {output_path}")
        

if __name__=="__main__":
    trainer = ModelTrainer()
    print("Model Trainer initialized.")