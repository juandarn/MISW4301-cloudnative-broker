from abc import ABC, abstractmethod


class MessageTopicPort(ABC):

    @abstractmethod
    def send_message(self, message: dict) -> None:
        """Send a message to a topic."""
        raise NotImplementedError("This method should be overridden by subclasses.")
