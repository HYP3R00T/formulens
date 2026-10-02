"""Validated Formulens preferences."""

from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    """Preferences for clipboard output and desktop notifications."""

    model_config = ConfigDict(extra="forbid")

    copy_to_clipboard: bool = True
    notifications: bool = True
