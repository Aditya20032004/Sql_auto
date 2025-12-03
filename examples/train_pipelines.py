import os
import logging
import sys
import tensorflow as tf

# Enable GPU memory growth to prevent loading entire dataset to VRAM at once
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(f"GPU config error: {e}")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from src.dataset_builder import SQLDatasetBuilder
from src.model_trainer import ModelTrainer
from src.core.logger import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("training pipeline...")
    
    builder = SQLDatasetBuilder()
    # builder.spider_dataset(max_examples=8000)

    builder.wiqiSQL_dataset(max_examples=10000,use_schema=True)
    dataset = builder.save_dataset(output_path="data/processed/wikisql_dataset")
    
    logger.info("Dataset saved..now starting training...")
    
    trainer = ModelTrainer(model_name_or_path="google/flan-t5-base",
                           dataset_path="data/processed/wikisql_dataset")
    
    history = trainer.train(epochs=30,
                            lr = 0.00015,
                            batch_size=1,
                            )
    logger.info("Training completed..now saving the model")
    trainer.save_model(output_path="models/trained_wikisql_model")
    # trainer.save_model(output_path="models/trained_sql_model")
    logger.info("Model saving sucessfull..")
    
if __name__=="__main__":
    main()