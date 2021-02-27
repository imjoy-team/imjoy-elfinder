"""Provide app settings."""
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Represent app settings."""

    root_dir: str = ""
    files_url: str = ""
    base_url: str = "/"
    expose_real_path: bool = False
    thumbnail_dir: Optional[str] = ".tmb"
    dot_files: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Return app settings lru cached."""
    return Settings()
