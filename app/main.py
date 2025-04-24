import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import pipeline

from app.logger import logger

app = FastAPI()

# Загружаем модель один раз при старте
logger.info("Loading model...")
classifier = pipeline(
    "text-classification", model="AbdulSami/bert-base-cased-cefr", device=-1
)
logger.info("Model loaded")


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1)


@app.post("/classify")
async def classify_text(req: TextRequest):
    word_count = len(req.text.split())
    if word_count > 500:
        raise HTTPException(status_code=400, detail="Максимум 500 слов")

    try:
        logger.info("Running inference...")
        with torch.no_grad():
            result = classifier(req.text)
        return {"result": result[0]["label"]}
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обработке текста")
