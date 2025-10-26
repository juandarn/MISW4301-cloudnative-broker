from domain.ports.message_topic import MessageTopicPort
from domain.use_cases.base_use_case import BaseUseCase


class PublisherUseCase(BaseUseCase):
    """Use case for producing messages."""

    message_topic: MessageTopicPort

    def __init__(self, message_topic: MessageTopicPort):
        self.message_topic = message_topic

    def execute(self, message: dict) -> None:
        """Execute the use case to send a message."""
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary.")
        self.message_topic.send_message(message)
