import json
import logging
import sys

from aws_lambda_powertools.utilities.data_classes import (
    SQSEvent,
    SQSRecord,
    event_source,
)

from config import AppConfig

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(AppConfig.log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logging.getLogger().setLevel(AppConfig.log_level)
logging.getLogger().addHandler(handler)


def process_record(record: SQSRecord):
    message = record.body
    message_id = record.message_id
    return message, message_id


# https://docs.powertools.aws.dev/lambda/python/latest/utilities/data_classes/#sqs
@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context):
    logging.info(f"Received event: {event}")
    # Multiple records can be delivered in a single event
    for record in event.records:
        message, message_id = process_record(record)
        json_message = json.loads(message)
        logging.info(f"Processed message ID: {message_id}, Body: {json_message}")

    return {
        "message": message,
        "message_id": message_id,
    }
