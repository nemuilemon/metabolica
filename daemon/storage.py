"""Storage module - S3 and DynamoDB persistence"""

import json
import logging
import os
from datetime import datetime, timezone, timedelta

import boto3

log = logging.getLogger("metabolica.storage")

JST = timezone(timedelta(hours=9))

S3_BUCKET = os.environ["S3_BUCKET"]
AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")

_s3 = boto3.client("s3", region_name=AWS_REGION)


def save_raw_collection(data: dict) -> str:
    """Save raw collected data to S3. Returns the S3 key."""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    timestamp = datetime.now(JST).strftime("%H%M%S")
    key = f"raw/{today}/collect_{timestamp}.json"

    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    _s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=body,
        ContentType="application/json; charset=utf-8",
    )
    log.info("Saved raw collection to s3://%s/%s (%d bytes)", S3_BUCKET, key, len(body))
    return key
