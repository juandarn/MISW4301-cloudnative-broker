from pydantic import BaseModel


class MessageRequest(BaseModel):

    times: int
    message: str
