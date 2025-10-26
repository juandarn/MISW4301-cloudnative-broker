from domain.ports.message_queue import MessageQueuePort
from domain.use_cases.base_use_case import BaseUseCase


class ProducerUseCase(BaseUseCase):
    """Use case for producing messages."""

    message_queue: MessageQueuePort

    def __init__(self, message_queue: MessageQueuePort):
        self.message_queue = message_queue

    def execute(self, message: dict, times: int) -> None:
        """Execute the use case to send a message multiple times."""
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary.")
        for _ in range(times):
            self.message_queue.send_message(message)
