import streamlit as st
from datetime import datetime, timedelta
import uuid

from src.db.postgres import get_recent_campaigns, get_campaign_summary, add_event, get_effectiveness


params = st.experimental_get_query_params()
if params.get("event") == ["click"]:
    cid = params.get("campaign_id", [""])[0]
    lock_id = params.get("lock_id", [""])[0]
    user_id = params.get("user_id", [""])[0]
    try:
        add_event(uuid.UUID(cid), "clicked", lock_id, user_id, None)
        st.write("Recorded click")
    except Exception as e:
        st.write("Error")

st.title("Lock Battery Campaign Metrics")
campaigns = get_recent_campaigns(limit=20)
rows = []
for c in campaigns:
    cid = uuid.UUID(c["campaign_id"]) if isinstance(c["campaign_id"], str) else c["campaign_id"]
    sent, clicked = get_campaign_summary(cid)
    rate = 0.0
    if sent:
        rate = (clicked / sent) * 100.0
    eff = get_effectiveness(cid)
    rows.append({
        "campaign_id": c["campaign_id"],
        "run_date": c["run_date"],
        "sent": sent,
        "clicked": clicked,
        "click_rate_%": round(rate, 2),
        "effective_rate_%": round(eff["rate"], 2) if eff else None,
    })
st.dataframe(rows)
