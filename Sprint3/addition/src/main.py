from fastapi import FastAPI

from models import AdditionInput


app = FastAPI()


@app.get("/add/ping", response_model=str)
def ping() -> str:
    """Health check endpoint."""
    return "pong"


@app.post("/add")
def add_numbers(input: AdditionInput):
    """Endpoint to add two numbers."""
    result = input.number1 + input.number2
    return {"result": result}