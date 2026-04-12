"""Storage module - S3 and DynamoDB persistence"""

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import boto3

log = logging.getLogger("metabolica.storage")

JST = timezone(timedelta(hours=9))

S3_BUCKET = os.environ["S3_BUCKET"]
DNA_CHAIN_TABLE = os.environ["DNA_CHAIN_TABLE"]
AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")

GENESIS_HASH = "0" * 64

_s3 = boto3.client("s3", region_name=AWS_REGION)
_ddb = boto3.resource("dynamodb", region_name=AWS_REGION)


def _to_ddb(obj):
    """Recursively convert floats to Decimal for DynamoDB compatibility."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _to_ddb(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_ddb(v) for v in obj]
    return obj


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


def save_dna_record(record: dict) -> str:
    """Save the full DNA record JSON to S3. Returns the S3 key."""
    day = record["day"]
    date = record["date"]
    time_str = record.get("time", "000000").replace(":", "")
    key = f"dna/{date}/day{day:04d}_{time_str}.json"

    body = json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8")
    _s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=body,
        ContentType="application/json; charset=utf-8",
    )
    log.info("Saved DNA record to s3://%s/%s (%d bytes)", S3_BUCKET, key, len(body))
    return key


# day=0 is reserved as the "latest pointer" metadata entry.
# This avoids needing dynamodb:Scan permission.
POINTER_DAY = 0


def get_latest_chain_entry() -> tuple[int, str]:
    """Get the most recent (day, raw_hash) via the pointer item. Genesis if empty."""
    table = _ddb.Table(DNA_CHAIN_TABLE)
    response = table.get_item(Key={"day": POINTER_DAY})
    item = response.get("Item")
    if not item:
        return 0, GENESIS_HASH
    return int(item.get("latest_day", 0)), str(item.get("latest_hash", GENESIS_HASH))


def append_dna_chain(record: dict) -> None:
    """Append a DNA record and update the latest-pointer atomically-ish."""
    table = _ddb.Table(DNA_CHAIN_TABLE)
    table.put_item(Item=_to_ddb(record))
    table.put_item(Item={
        "day": POINTER_DAY,
        "latest_day": record["day"],
        "latest_hash": record["raw_hash"],
    })
    log.info("Appended day %d to DynamoDB chain", record["day"])


def upload_log(log_text: str, day: int, now: datetime) -> str:
    """Upload a cycle's log to S3. Returns the S3 key."""
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M%S")
    key = f"logs/{date_str}/day{day:04d}_{time_str}.log"

    _s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=log_text.encode("utf-8"),
        ContentType="text/plain; charset=utf-8",
    )
    log.info("Uploaded log to s3://%s/%s", S3_BUCKET, key)
    return key
