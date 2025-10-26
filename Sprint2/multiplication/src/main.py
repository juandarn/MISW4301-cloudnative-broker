import os
import requests
from fastapi import FastAPI, HTTPException
from models import MultiplicationInput

app = FastAPI()


ADDITION_URL = os.getenv("ADDITION_URL")

@app.post("/multiply")
async def multiply(input: MultiplicationInput):
    """Endpoint to multiply two numbers using addition."""

    total = 0.0
    for _ in range(input.number2):

        response = await requests.post(
            ADDITION_URL,
            json={"number1": total, "number2": input.number1}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Failed to call addition service")
        total = response.json()["result"]

    return {"result": total}