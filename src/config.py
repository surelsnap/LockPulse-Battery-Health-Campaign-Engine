import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMO_TABLE_LOCKS = os.getenv("DYNAMO_TABLE_LOCKS", "locks")
LOCK_LAST_CHECK_FIELD = os.getenv("LOCK_LAST_CHECK_FIELD", "last_checked")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "cloudbackend")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

CAMPAIGN_CLICK_URL = os.getenv("CAMPAIGN_CLICK_URL", "http://localhost:8501/")

DEFAULT_NOTIFICATION_TITLE = os.getenv("DEFAULT_NOTIFICATION_TITLE", "Check your lock battery")
DEFAULT_NOTIFICATION_BODY = os.getenv("DEFAULT_NOTIFICATION_BODY", "It’s been a month since the last check.")

NOTIFICATION_MONTHS_THRESHOLD = int(os.getenv("NOTIFICATION_MONTHS_THRESHOLD", "1"))
EFFECTIVENESS_WINDOW_DAYS = int(os.getenv("EFFECTIVENESS_WINDOW_DAYS", "7"))

