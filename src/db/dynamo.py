import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Attr

from src.config import AWS_REGION, DYNAMO_TABLE_LOCKS, LOCK_LAST_CHECK_FIELD, NOTIFICATION_MONTHS_THRESHOLD


def _parse_ts(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        try:
            return datetime.fromisoformat(str(v)).timestamp()
        except Exception:
            return 0.0


def get_locks_needing_check(now: datetime | None = None) -> List[Dict[str, Any]]:
    client = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = client.Table(DYNAMO_TABLE_LOCKS)

    now_dt = now or datetime.utcnow()
    cutoff = now_dt - timedelta(days=NOTIFICATION_MONTHS_THRESHOLD * 30)

    # ❗ FIX: DynamoDB CANNOT accept float, must be Decimal
    cutoff_ts = Decimal(str(cutoff.timestamp()))

    fe = Attr(LOCK_LAST_CHECK_FIELD).lt(cutoff_ts)
    resp = table.scan(FilterExpression=fe)

    return resp.get("Items", [])


def get_locks_checked_since(lock_ids: List[str], since: datetime) -> List[str]:
    client = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = client.Table(DYNAMO_TABLE_LOCKS)

    checked = []

    # since.timestamp() is okay because we compare internally, not send to Dynamo
    since_ts = since.timestamp()

    for lock_id in lock_ids:
        r = table.get_item(Key={"lock_id": lock_id})
        item = r.get("Item")
        if not item:
            continue
        v = item.get(LOCK_LAST_CHECK_FIELD)
        if _parse_ts(v) >= since_ts:
            checked.append(lock_id)

    return checked


