import threading


class Settings(threading.local):
    DEFAULT_CLIENT = None


settings = Settings()