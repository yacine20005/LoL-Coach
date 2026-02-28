import os

from dotenv import load_dotenv

load_dotenv()


def get_required_env_var(name: str) -> str:
    """Return the value of a required environment variable, raising if absent."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_int_env_var(name: str, default: int) -> int:
    """Return an environment variable as an integer, falling back to *default*."""
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {name}: {value}") from exc


def get_optional_env_var(name: str, default: str = "") -> str:
    """Return an optional environment variable, falling back to *default*."""
    return os.getenv(name, default) or default
