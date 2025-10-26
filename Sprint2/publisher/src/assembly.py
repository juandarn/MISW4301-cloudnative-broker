from functools import lru_cache

from adapters.sns_message_topic import SNSMessageTopicAdapter
from config import AppConfig
from domain.use_cases.base_use_case import BaseUseCase
from domain.use_cases.publisher_use_case import PublisherUseCase


@lru_cache()
def build_use_case() -> BaseUseCase:
    """Get use case."""

    topic_arn = AppConfig.message_topic_arn
    message_topic = SNSMessageTopicAdapter(sns_topic_arn=topic_arn)

    return PublisherUseCase(message_topic)
