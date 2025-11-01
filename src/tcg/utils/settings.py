"""Application settings loader for CLI and API components."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AppSection(BaseModel):
    project_name: str = "Test Case Generator"
    environment: str = "development"
    default_seed: int = 424242
    output_dir: Path = Field(default=Path("output"))
    ai_provider: str = "openai"
    enable_local_llm: bool = False


class SecuritySection(BaseModel):
    jwt_secret_key: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


class AISection(BaseModel):
    provider: str = "openai"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4.1-mini"
    local_endpoint: Optional[str] = None
    local_auth_token: Optional[str] = None


class ScraperSection(BaseModel):
    rate_limit_per_minute: int = 30
    cache_dir: Path = Path("cache")
    user_agent: str = "tcg-bot/0.1"


class ExecutorSection(BaseModel):
    max_cpu_time_sec: float = 2.0
    max_memory_mb: int = 256
    sandbox: str = "none"


class LoggingSection(BaseModel):
    level: str = "INFO"
    file: Path = Path("logs/app.log")


class Settings(BaseModel):
    app: AppSection = AppSection()
    security: SecuritySection = SecuritySection()
    ai: AISection = AISection()
    scraper: ScraperSection = ScraperSection()
    executor: ExecutorSection = ExecutorSection()
    logging: LoggingSection = LoggingSection()

    @property
    def output_dir(self) -> Path:
        return self.app.output_dir


def load_settings(path: Path | None = None) -> Settings:
    """Load settings from TOML configuration and environment overrides."""

    candidate_path = path or Path("config/settings.toml")
    data: Dict[str, Any] = {}

    if candidate_path.exists():
        data = _load_toml(candidate_path)

    env_overrides = _build_env_overrides()
    merged = _merge_dicts(data, env_overrides)

    return Settings.model_validate(merged)


def _load_toml(path: Path) -> Dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _build_env_overrides() -> Dict[str, Any]:
    overrides: Dict[str, Any] = {}

    if secret := os.getenv("TCG_JWT_SECRET_KEY"):
        overrides.setdefault("security", {})["jwt_secret_key"] = secret

    if key := os.getenv("OPENAI_API_KEY"):
        overrides.setdefault("ai", {})["openai_api_key"] = key

    if output_dir := os.getenv("TCG_OUTPUT_DIR"):
        overrides.setdefault("app", {})["output_dir"] = output_dir

    return overrides


def _merge_dicts(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
