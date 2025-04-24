import torch
from transformers import pipeline

from app.logger import logger

# Загружаем один раз
classifier = pipeline(
    "text-classification", model="AbdulSami/bert-base-cased-cefr", device=-1
)


def classify_text_sync(text: str):
    try:
        logger.info("Running inference...")
        with torch.no_grad():
            result = classifier(text)
        return {"label": result[0]["label"], "score": result[0]["score"]}
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return {"error": str(e)}
