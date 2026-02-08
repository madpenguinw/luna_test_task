import enum
import json
import os
from datetime import date
from functools import lru_cache
from typing import Any

import attrs
import dotenv
import environ


def _str_to_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return value.lower() in ("true", "1", "yes")


@environ.config(prefix="APP")
class Config:
    @environ.config
    class Postgres:
        @environ.config
        class Credentials:
            database: str = environ.var(default="directory")
            user: str = environ.var(default="postgres")
            password: str = environ.var(default="postgres")
            host: str = environ.var(default="127.0.0.1")
            port: int = environ.var(default=5432, converter=int)
            pool_size: int = environ.var(default=5, converter=int)
            pool_max_overflow: int = environ.var(default=2, converter=int)
            pool_recycle: int = environ.var(default=1200, converter=int)

            @property
            def database_url(self) -> str:
                return (
                    f"postgresql+asyncpg://{self.user}:{self.password}"
                    f"@{self.host}:{self.port}/{self.database}"
                )

        data = environ.group(Credentials)

    @environ.config
    class App:
        title: str = environ.var(default="Organization Directory API")
        version: str = environ.var(default="1.0.0")
        debug: bool = environ.var(default=False, converter=_str_to_bool)

    @environ.config
    class Security:
        api_key: str = environ.var(default="secret-api-key")

    @environ.config
    class Activity:
        max_depth: int = environ.var(default=3, converter=int)

    postgres: Postgres = environ.group(Postgres)
    app: App = environ.group(App)
    security: Security = environ.group(Security)
    activity: Activity = environ.group(Activity)

    @classmethod
    def load(cls) -> "Config":
        dotenv.load_dotenv()
        return environ.to_config(config_cls=cls, environ=dict(os.environ))


def config_to_env_dict(  # noqa: C901
    config_obj: Config,
    prefix: str = "APP",
    separator: str = "_",
    nested_separator: str = "_",
) -> dict[str, Any]:
    """Convert a Config object into a flat dict of environment variables."""
    result: dict[str, Any] = {}

    def _process_object(obj: Any, current_path: str | None = None) -> None:
        if not attrs.has(obj.__class__):
            return

        for field in attrs.fields(cls=obj.__class__):
            value: Any | None = getattr(obj, field.name, None)
            path_parts: list[str | None] = [current_path, field.name.upper()]
            full_path: str = nested_separator.join(filter(None, path_parts))

            match value:
                case _ if attrs.has(value.__class__):
                    _process_object(obj=value, current_path=full_path)
                case None:
                    continue
                case _:
                    env_key = f"{prefix}{separator}{full_path}"
                    match value:
                        case dict() | list():
                            val_to_store: str = json.dumps(obj=value)
                        case date():
                            val_to_store = value.isoformat()
                        case enum.Enum():
                            val_to_store = value.value
                        case _:
                            val_to_store = value
                    result[env_key] = val_to_store

    _process_object(obj=config_obj)
    return result


@lru_cache(maxsize=1)
def load_config() -> Config:
    return Config.load()


config = load_config()
