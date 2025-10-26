from pydantic import BaseModel


class AdditionInput(BaseModel):
    number1: float
    number2: float