
import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "local-development-secret-key"
    )

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
