"""Load and save user configuration through UtilityHub Config."""

import tomllib
from pathlib import Path

from utilityhub_config import ensure_config_file, get_config_path, load_settings, write_config

from formulens.configuration.schema import Settings


def get_settings_path() -> Path:
    return get_config_path("formulens")


def initialize_settings() -> Path:
    """Create defaults without overwriting an existing configuration."""
    path = get_settings_path()
    if path.exists():
        read_saved_settings()
    return ensure_config_file(Settings(), "formulens")


def read_saved_settings() -> Settings:
    """Read only persisted values, so edits never save environment overrides."""
    path = get_settings_path()
    if not path.exists():
        return Settings()
    with path.open("rb") as stream:
        return Settings.model_validate(tomllib.load(stream))


def load_configuration() -> Settings:
    """Resolve settings without discovering files in the current directory."""
    settings, _ = load_settings(
        Settings,
        app_name="formulens",
        cwd=get_settings_path().parent,
        env_prefix="FORMULENS",
    )
    return settings


def set_setting(key: str, value: str) -> Path:
    """Validate a single edit before writing the saved configuration."""
    if key not in Settings.model_fields:
        raise ValueError(f"Unknown setting '{key}'. Choose from: {', '.join(Settings.model_fields)}")
    values = read_saved_settings().model_dump()
    values[key] = value
    settings = Settings.model_validate(values)
    return write_config(settings, "formulens")
