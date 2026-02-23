import os

from dotenv import load_dotenv

load_dotenv()


def get_required_env_var(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_int_env_var(name, default):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {name}: {value}") from exc


def get_optional_env_var(name, default=""):
    value = os.getenv(name, default)
    if value is None:
        return default
    return value
