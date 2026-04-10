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
    key = f"dna/{date}_day{day:04d}.json"

    body = json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8")
    _s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=body,
        ContentType="application/json; charset=utf-8",
    )
    log.info("Saved DNA record to s3://%s/%s (%d bytes)", S3_BUCKET, key, len(body))
    return key


def get_latest_chain_entry() -> tuple[int, str]:
    """Get the most recent (day, raw_hash) from the DNA chain. Genesis if empty."""
    table = _ddb.Table(DNA_CHAIN_TABLE)
    response = table.scan(
        ProjectionExpression="#d, raw_hash",
        ExpressionAttributeNames={"#d": "day"},
    )
    items = response.get("Items", [])
    if not items:
        return 0, GENESIS_HASH
    latest = max(items, key=lambda x: int(x["day"]))
    return int(latest["day"]), str(latest.get("raw_hash", GENESIS_HASH))


def append_dna_chain(record: dict) -> None:
    """Append a DNA record to the DynamoDB chain table."""
    table = _ddb.Table(DNA_CHAIN_TABLE)
    table.put_item(Item=_to_ddb(record))
    log.info("Appended day %d to DynamoDB chain", record["day"])
