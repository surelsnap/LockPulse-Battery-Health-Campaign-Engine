from typing import Optional, Dict
import uuid

from firebase_admin import messaging, credentials, initialize_app, _apps

from src.config import GOOGLE_APPLICATION_CREDENTIALS, CAMPAIGN_CLICK_URL


def _ensure_app():
    if not _apps:
        cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
        initialize_app(cred)


def send_notification(token: str, title: str, body: str, campaign_id: uuid.UUID, lock_id: str, user_id: str) -> Optional[str]:
    _ensure_app()
    url = f"{CAMPAIGN_CLICK_URL}?event=click&campaign_id={campaign_id}&lock_id={lock_id}&user_id={user_id}"
    msg = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data={
            "campaign_id": str(campaign_id),
            "lock_id": lock_id,
            "user_id": user_id,
            "click_url": url,
        },
        android=messaging.AndroidConfig(notification=messaging.AndroidNotification(click_action=url)),
        apns=messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(custom_data={"url": url}))),
    )
    resp = messaging.send(msg)
    return resp

