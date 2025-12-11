from typing import List, Dict, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from datetime import datetime

from src.config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)


def get_conn():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def get_users_for_locks(lock_ids: List[str]) -> List[Dict[str, Any]]:
    if not lock_ids:
        return []
    q = """
        select lock_id, user_id, fcm_id
        from lock_user_mapping
        where lock_id = any(%s)
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q, (lock_ids,))
            rows = cur.fetchall()
            return list(rows)


def create_campaign(run_date: datetime, title: str, body: str, lock_count: int) -> uuid.UUID:
    cid = uuid.uuid4()
    q = """
        insert into notification_campaigns(campaign_id, run_date, title, body, lock_count)
        values (%s, %s, %s, %s, %s)
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (str(cid), run_date, title, body, lock_count))
    return cid


def add_event(
    campaign_id: uuid.UUID,
    event_type: str,
    lock_id: Optional[str],
    user_id: Optional[str],
    fcm_message_id: Optional[str],
    at: Optional[datetime] = None,
) -> None:
    q = """
        insert into notification_events(campaign_id, event_type, lock_id, user_id, fcm_message_id, event_time)
        values (%s, %s, %s, %s, %s, %s)
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (str(campaign_id), event_type, lock_id, user_id, fcm_message_id, at or datetime.utcnow()))


def get_campaign_summary(campaign_id: uuid.UUID) -> Tuple[int, int]:
    q_sent = """
        select count(*) from notification_events
        where campaign_id = %s and event_type = 'sent'
    """
    q_clicked = """
        select count(distinct user_id) from notification_events
        where campaign_id = %s and event_type = 'clicked'
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q_sent, (str(campaign_id),))
            sent = cur.fetchone()[0]
            cur.execute(q_clicked, (str(campaign_id),))
            clicked = cur.fetchone()[0]
    return sent, clicked


def get_recent_campaigns(limit: int = 12) -> List[Dict[str, Any]]:
    q = """
        select campaign_id, run_date, title, body, lock_count
        from notification_campaigns
        order by run_date desc
        limit %s
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q, (limit,))
            return list(cur.fetchall())


def get_campaign_lock_ids(campaign_id: uuid.UUID) -> List[str]:
    q = """
        select distinct lock_id from notification_events
        where campaign_id = %s and event_type = 'sent' and lock_id is not null
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (str(campaign_id),))
            rows = cur.fetchall()
            return [r[0] for r in rows]


def upsert_effectiveness(campaign_id: uuid.UUID, targets: int, checked: int, rate: float) -> None:
    q = """
        insert into notification_effectiveness(campaign_id, targets, checked, rate, snapshot_time)
        values (%s, %s, %s, %s, now())
        on conflict (campaign_id) do update set targets = excluded.targets, checked = excluded.checked, rate = excluded.rate, snapshot_time = excluded.snapshot_time
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (str(campaign_id), targets, checked, rate))


def get_effectiveness(campaign_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    q = """
        select targets, checked, rate, snapshot_time from notification_effectiveness where campaign_id = %s
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q, (str(campaign_id),))
            row = cur.fetchone()
            return dict(row) if row else None
