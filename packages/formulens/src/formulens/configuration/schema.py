"""Validated Formulens preferences."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Settings(BaseModel):
    """Preferences for recognition, model storage, and desktop output."""

    model_config = ConfigDict(extra="forbid")

    copy_to_clipboard: bool = True
    notifications: bool = True
    model: Literal["paddle", "got"] = "paddle"
    model_directory: str = "~/.config/formulens/models"
    device: Literal["cuda"] = "cuda"
    max_tokens: int = Field(default=1024, ge=16, le=4096)

    def get_model_directory(self) -> Path:
        return Path(self.model_directory).expanduser().resolve()
