import uuid
from datetime import datetime, timedelta
from typing import List

from src.config import DEFAULT_NOTIFICATION_TITLE, DEFAULT_NOTIFICATION_BODY, EFFECTIVENESS_WINDOW_DAYS
from src.db.dynamo import get_locks_needing_check, get_locks_checked_since
from src.db.postgres import get_users_for_locks, create_campaign, add_event, get_recent_campaigns, get_campaign_summary, get_campaign_lock_ids, upsert_effectiveness
from src.notifications.fcm import send_notification


def run_campaign():
    now = datetime.utcnow()
    locks = get_locks_needing_check(now)
    lock_ids = [str(l.get("lock_id")) for l in locks if l.get("lock_id")]
    cid = create_campaign(now, DEFAULT_NOTIFICATION_TITLE, DEFAULT_NOTIFICATION_BODY, len(lock_ids))
    mappings = get_users_for_locks(lock_ids)
    for m in mappings:
        token = m.get("fcm_id")
        if not token:
            continue
        rid = send_notification(token, DEFAULT_NOTIFICATION_TITLE, DEFAULT_NOTIFICATION_BODY, cid, str(m.get("lock_id")), str(m.get("user_id")))
        add_event(cid, "sent", str(m.get("lock_id")), str(m.get("user_id")), rid)
    sent, clicked = get_campaign_summary(cid)
    return cid, sent, clicked


def compute_effectiveness_for_recent_campaigns():
    campaigns = get_recent_campaigns(limit=4)
    for c in campaigns:
        cid = uuid.UUID(c["campaign_id"]) if isinstance(c["campaign_id"], str) else c["campaign_id"]
        window_start = c["run_date"]
        window_end = window_start + timedelta(days=EFFECTIVENESS_WINDOW_DAYS)
        lock_ids = get_campaign_lock_ids(cid)
        lock_count = len(lock_ids)
        checked = get_locks_checked_since(lock_ids, window_start)
        rate = 0.0
        if lock_count:
            rate = (len(checked) / lock_count) * 100.0
        upsert_effectiveness(cid, lock_count, len(checked), rate)
    return True


if __name__ == "__main__":
    cid, sent, clicked = run_campaign()
    compute_effectiveness_for_recent_campaigns()
    print(str(cid))
    print(str(sent))
    print(str(clicked))
