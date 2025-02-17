import os


class Config:
    # SQLALCHEMY_DATABASE_URI = "CENSORED"
    SQLALCHEMY_DATABASE_URI = "CENSORED"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "CENSORED"
    SESSION_TYPE="filesystem"
    SESSION_PERMANENT=False
    JWT_SECRET_KEY="CENSORED"
    CAPTCHA_SECRET="CENSORED"
    USER_TIMEOUT_DURATION_IN_SECONDS = 10 * 60
    USER_MAXIMUM_ATTEMPTS = 3
    SAFE_MIMETYPES = ["image/jpeg", "image/png", "text/plain"]
    PASSWORD_REGEX = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,64}$'
    EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    DEFAULT_RATE_LIMITS = ["10/minute"]
    MAX_CONTENT_LENGTH = 4294967295
    TOTP_VERIFIED_COUNT = 5
    DEFAULT_PAGINATION_MAX_ROWS = 50
    MAIL_SERVER = 'CENSORED'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'CENSORED'
    MAIL_PASSWORD = 'CENSORED'
    VIRUS_TOTAL_KEY = 'CENSORED'
