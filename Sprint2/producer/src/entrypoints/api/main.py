import logging
import sys

from assembly import build_use_case
from config import AppConfig

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from domain.use_cases.base_use_case import BaseUseCase
from entrypoints.api.models import MessageRequest


handler = logging.StreamHandler(sys.stdout)
handler.setLevel(AppConfig.log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logging.getLogger().setLevel(AppConfig.log_level)
logging.getLogger().addHandler(handler)


app = FastAPI()

@app.get("/producer/ping", response_model=str)
def ping() -> str:
    """Health check endpoint."""
    return "pong"


@app.post("/producer/send")
def send(
    req: MessageRequest,
    use_case: BaseUseCase = Depends(build_use_case),
):
    """Endpoint to multiply two numbers using addition."""

    use_case.execute({"message": req.message}, req.times)
    return JSONResponse(
        status_code=200,
        content={"data": {"result": f"Message sent successfully {req.times} times"}},
    )
