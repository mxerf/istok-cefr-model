from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.logger import logger
from app.sqlite_cache import check_cache, init_db, save_pending  # 🔥
from app.worker import classify_text_task

app = FastAPI()

init_db()  # 👈 один раз при старте приложения


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1)


@app.post("/classify")
async def classify(req: TextRequest):
    word_count = len(req.text.split())
    if word_count > 500:
        raise HTTPException(
            status_code=400, detail=f"Too long: {word_count} words (max 500)"
        )

    cached = check_cache(req.text)
    if cached:
        logger.info("Cache hit — skipping task creation")
        return {"status": "done", "result": cached, "cached": True}

    save_pending(req.text)
    task = classify_text_task.delay(req.text)
    logger.info(f"Task {task.id} queued")
    return {"task_id": task.id, "cached": False}


@app.get("/result/{task_id}")
def get_result(task_id: str):
    from app.worker import celery_app

    task = celery_app.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "SUCCESS":
        return {"status": "done", "result": task.result}
    else:
        return {"status": task.state.lower(), "error": str(task.info)}
