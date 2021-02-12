from functools import lru_cache
from pydantic import BaseSettings
from typing import Any, Dict, List, Optional


class Settings(BaseSettings):
    root_dir: str = ""
    files_url: str = ""
    base_url: str = "/"
    expose_real_path: bool = False
    thumbnail_dir: Optional[str] = ".tmb"
    dot_files: bool = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
