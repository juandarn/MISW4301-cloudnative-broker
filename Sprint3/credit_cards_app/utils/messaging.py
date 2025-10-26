# utils/messaging.py
from __future__ import annotations
import os, json, time
import boto3

_REGION = os.environ.get("AWS_REGION", "us-east-1")
_QUEUE_URL = os.environ.get("CARDS_QUEUE_URL", "")

# Si el nodo/IRSA tiene permisos, NO necesitas AccessKey/Secret:
_sqs = boto3.client("sqs", region_name=_REGION)

def publish_card_created(*, ruv: str, card_id: str, user_id: str) -> None:
    """
    Envía un evento mínimo para que el worker consulte TrueNative y actualice la BD.
    """
    if not _QUEUE_URL:
        # Si no hay cola configurada, salimos silenciosamente (no tronamos la request)
        return
    payload = {
        "type": "card_created",
        "ruv": ruv,
        "cardId": card_id,
        "userId": user_id,
        "ts": int(time.time())
    }
    _sqs.send_message(QueueUrl=_QUEUE_URL, MessageBody=json.dumps(payload))
