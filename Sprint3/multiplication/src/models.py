from pydantic import BaseModel


class MultiplicationInput(BaseModel):
    number1: float
    number2: int