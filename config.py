
import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "local-development-secret-key"
    )

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Email configuration

    MAIL_ENABLED = os.environ.get(
        "MAIL_ENABLED", "true"
    ).lower() == "true"

    MAIL_SERVER = os.environ.get(
        "MAIL_SERVER", "127.0.0.1"
    )

    MAIL_PORT = int(
        os.environ.get("MAIL_PORT", "1025")
    )

    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")

    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    MAIL_USE_TLS = os.environ.get(
        "MAIL_USE_TLS", "false"
    ).lower() == "true"

    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        "notifications@socialspace.example"
    )
