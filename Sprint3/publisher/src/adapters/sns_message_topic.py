import json
import logging

import boto3

from domain.ports.message_topic import MessageTopicPort
from errors import IntegrationError


class SNSMessageTopicAdapter(MessageTopicPort):

    def __init__(self, sns_topic_arn: str):
        self.sns_client = boto3.client("sns")
        self.sns_topic_arn = sns_topic_arn

    def send_message(self, message: dict) -> None:
        """Send a message to the SNS topic."""
        response = self.sns_client.publish(
            TopicArn=self.sns_topic_arn,
            Message=json.dumps(message),
            Subject="Message from Publisher Lambda" # Subject for SNS notifications
        )
        logging.info(f"Message sent to SNS: {message}, Response: {response}")
        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200:
            logging.error(f"Failed to send message to SNS: {response}")
            raise IntegrationError("Failed to send message to SNS")
