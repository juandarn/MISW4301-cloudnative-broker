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
    def message_topic_arn(cls) -> str:
        """Return the message topic ARN based on the environment."""
        return os.environ.get("MESSAGE_TOPIC_ARN")
