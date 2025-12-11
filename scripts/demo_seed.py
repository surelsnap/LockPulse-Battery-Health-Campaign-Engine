from datetime import datetime
import uuid

from src.db.postgres import get_conn, create_campaign, add_event


def ensure_lock_user_mapping():
    q = """
        create table if not exists lock_user_mapping (
            lock_id varchar(128) not null,
            user_id varchar(128) not null,
            fcm_id varchar(256),
            primary key(lock_id, user_id)
        )
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q)


def seed_mapping(n: int = 5):
    with get_conn() as conn:
        with conn.cursor() as cur:
            for i in range(n):
                cur.execute(
                    "insert into lock_user_mapping(lock_id, user_id, fcm_id) values (%s, %s, %s) on conflict do nothing",
                    (f"LOCK-{i+1}", f"USER-{i+1}", None),
                )


def seed_campaign():
    cid = create_campaign(datetime.utcnow(), "Demo", "Demo body", 5)
    for i in range(5):
        add_event(cid, "sent", f"LOCK-{i+1}", f"USER-{i+1}", f"MSG-{i+1}")
    add_event(cid, "clicked", "LOCK-1", "USER-1", None)
    add_event(cid, "clicked", "LOCK-2", "USER-2", None)
    print(str(cid))


if __name__ == "__main__":
    ensure_lock_user_mapping()
    seed_mapping()
    seed_campaign()

