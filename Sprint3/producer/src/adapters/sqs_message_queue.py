import json
import logging

import boto3

from domain.ports.message_queue import MessageQueuePort
from errors import IntegrationError


class SQSMessageQueueAdapter(MessageQueuePort):

    def __init__(self, queue_url: str):
        self.sqs_client = boto3.client("sqs")
        self.queue_url = queue_url

    def send_message(self, message: dict) -> None:
        """Send a message to the SQS queue."""
        response = self.sqs_client.send_message(
            QueueUrl=self.queue_url, MessageBody=json.dumps(message)
        )
        logging.info(f"Message sent to SQS: {message}, Response: {response}")
        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200:
            logging.error(f"Failed to send message to SQS: {response}")
            raise IntegrationError("Failed to send message to SQS")
