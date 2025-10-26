from functools import lru_cache

from adapters.sqs_message_queue import SQSMessageQueueAdapter
from config import AppConfig
from domain.use_cases.base_use_case import BaseUseCase
from domain.use_cases.producer_use_case import ProducerUseCase


@lru_cache()
def build_use_case() -> BaseUseCase:
    """Get use case."""

    queue_url = AppConfig.message_queue_url
    message_queue = SQSMessageQueueAdapter(queue_url=queue_url)

    return ProducerUseCase(message_queue)
