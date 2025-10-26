import logging
import sys

from aws_lambda_powertools.utilities.data_classes import SNSEvent, event_source

from config import AppConfig

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(AppConfig.log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)
logging.getLogger().setLevel(AppConfig.log_level)
logging.getLogger().addHandler(log_handler)


@event_source(data_class=SNSEvent)
def handler(event: SNSEvent, context):
    # Multiple records can be delivered in a single event
    logging.info(f"Received SNS event: {event}")
    for record in event.records:
        message = record.sns.message
        subject = record.sns.subject
        logging.info(f"Received message: {message}, Subject: {subject}")
    return {
        "message": message,
        "subject": subject,
    }