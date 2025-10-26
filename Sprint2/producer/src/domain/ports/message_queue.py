from abc import ABC, abstractmethod


class MessageQueuePort(ABC):

    @abstractmethod
    def send_message(self, message: dict) -> None:
        """Send a message to the message queue."""
        raise NotImplementedError("This method should be overridden by subclasses.")
