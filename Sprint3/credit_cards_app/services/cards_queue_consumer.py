from __future__ import annotations
import importlib, json, os
from typing import Any, Iterable

PROVIDER = os.environ.get("EVENT_QUEUE_PROVIDER", "off").lower()

_boto3_spec = importlib.util.find_spec("boto3")
boto3 = importlib.import_module("boto3") if _boto3_spec else None

class CardsQueueConsumer:
    """
    Consumer seguro:
    - off (default): no hace nada, yield vacíos.
    - sqs: lee de SQS usando CARDS_QUEUE_URL + credenciales.
    """
    def __init__(self, queue_url: str | None = None, client: Any | None = None):
        self.provider = PROVIDER
        self.queue_url = queue_url or os.environ.get("CARDS_QUEUE_URL")

        if self.provider == "off":
            self.client = None
            return

        if self.provider == "sqs":
            if not self.queue_url:
                raise RuntimeError("CARDS_QUEUE_URL is not configured")
            if boto3 is None and client is None:
                raise RuntimeError("boto3 is required to consume messages")
            self.client = client or boto3.client(
                "sqs",
                region_name=os.environ.get("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            )
        else:
            raise RuntimeError(f"Unsupported EVENT_QUEUE_PROVIDER: {self.provider}")

    def fetch_messages(self, max_messages: int = 5, wait_time: int = 10) -> Iterable[dict[str, Any]]:
        if self.provider == "off":
            return []  # no-op
        # SQS
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time,
            VisibilityTimeout=30,
        )
        for message in response.get("Messages", []):
            body = message.get("Body")
            try:
                payload = json.loads(body)
            except Exception:
                payload = {"raw": body}
            yield {"payload": payload, "receipt_handle": message.get("ReceiptHandle")}

    def delete_message(self, receipt_handle: str) -> None:
        if self.provider == "off":
            return  # no-op
        self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
