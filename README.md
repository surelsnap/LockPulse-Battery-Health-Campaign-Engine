# LockPulse-Battery-Health-Campaign-Engine

## Overview
- Sends FCM notifications to users mapped to locks whose battery check timestamp is older than 1 month.
- Runs weekly and stores campaign and event data in PostgreSQL for reporting.
- Reads lock timestamps from DynamoDB `locks` table.
- Streamlit dashboard shows sent, clicks, and click-through rate, and captures click events via a URL.

## Structure
- `src/config.py`: environment configuration
- `src/db/dynamo.py`: DynamoDB access
- `src/db/postgres.py`: PostgreSQL access and campaign/event logic
- `src/notifications/fcm.py`: FCM sender
- `scripts/run_weekly_campaign.py`: weekly job entrypoint
- `scripts/demo_seed.py`: demo data seeding
- `db/migrations/001_init.sql`: campaign tables
- `streamlit_app.py`: dashboard and click tracking
- `requirements.txt`: dependencies
- `.env.example`: environment variables template

## Prerequisites
- Python 3.11+
- AWS credentials configured with access to DynamoDB `locks`
- PostgreSQL
- Firebase service account JSON for FCM

## Setup
- Create a Python venv and install dependencies
  - `python -m venv .venv`
  - `.\.venv\Scripts\activate`
  - `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and fill values
- Create PostgreSQL tables
  - `psql -h <host> -U <user> -d <db> -f db/migrations/001_init.sql`
  - Ensure `lock_user_mapping` exists with columns `lock_id`, `user_id`, `fcm_id`

## Weekly Job
- Run once to validate
  - `python scripts/run_weekly_campaign.py`
- Schedule weekly on Windows Task Scheduler
  - Action: `Program/script`=`python`
  - Add arguments: `scripts/run_weekly_campaign.py`
  - Start in: project root

## Streamlit Dashboard
- Start dashboard
  - `streamlit run streamlit_app.py`
- Open `http://localhost:8501/`
- The dashboard records clicks when users visit the `CAMPAIGN_CLICK_URL` with params
  - Example click URL used in notifications: `http://localhost:8501/?event=click&campaign_id=<id>&lock_id=<lock>&user_id=<user>`

## Demo
- Seed sample data
  - `python scripts/demo_seed.py`
- Start dashboard and inspect metrics

## Measuring Effectiveness
- Effectiveness is defined as the share of targeted locks that show a battery check within `EFFECTIVENESS_WINDOW_DAYS` after notification.
- The weekly job stores snapshots and the dashboard surfaces campaign metrics.

## Notes
- DynamoDB field name for last check is `LOCK_LAST_CHECK_FIELD`.
- FCM credentials must be set in `GOOGLE_APPLICATION_CREDENTIALS`.
