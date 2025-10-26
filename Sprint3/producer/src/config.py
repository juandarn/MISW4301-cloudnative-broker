import os


class AppConfig:
    """Configuration for the application."""

    @classmethod
    @property
    def log_level(cls) -> str:
        """Return the log level based on the environment."""
        return os.environ.get("LOG_LEVEL", "DEBUG")

    @classmethod
    @property
    def message_queue_url(cls) -> str:
        """Return the message queue URL based on the environment."""
        return os.environ.get("SQS_QUEUE_URL")
