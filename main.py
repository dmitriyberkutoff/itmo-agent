import json
import time
from typing import List
from pydantic import HttpUrl
from fastapi import FastAPI, HTTPException, Request, Response
from schemas.request import PredictionRequest, PredictionResponse
from utils.logger import setup_logger, log_info, log_error
from model import search_and_answer

# Initialize
app = FastAPI()
logger = None
model_info = ' Информация была получена с помощью YandexGPT.'


@app.on_event("startup")
async def startup_event():
    global logger
    logger = await setup_logger()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    body = await request.body()
    await log_info(
        f"Incoming request: {request.method} {request.url}\n"
        f"Request body: {body.decode()}"
    )

    response = await call_next(request)
    process_time = time.time() - start_time

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    await log_info(
        f"Request completed: {request.method} {request.url}\n"
        f"Status: {response.status_code}\n"
        f"Response body: {response_body.decode()}\n"
        f"Duration: {process_time:.3f}s"
    )

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


@app.post("/api/request", response_model=PredictionResponse)
async def predict(body: PredictionRequest):
    try:
        await log_info(f"Processing prediction request with id: {body.id}")

        llm_answer = await search_and_answer(body.query)
        json_answer = json.loads(llm_answer)

        answer = json_answer['answer'] if json_answer['answer'] != 0 else None
        reasoning = json_answer['reasoning'] + model_info
        sources: List[HttpUrl] = [
            HttpUrl(link) for link in json_answer['sources']
        ]

        response = PredictionResponse(
            id=body.id,
            answer=answer,
            reasoning=reasoning,
            sources=sources,
        )

        await log_info(f"Successfully processed request {body.id}")

        return response
    except ValueError as e:
        error_msg = str(e)
        await log_error(f"Validation error for request {body.id}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        await log_error(f"Internal error processing request {body.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
