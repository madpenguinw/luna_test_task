import environ

from src.core.config import Config, config_to_env_dict


class TestConfig:
    def test_default_values(self) -> None:
        """Config loads with defaults when no env vars are set."""
        env = {
            "APP_POSTGRES_DATA_DATABASE": "testdb",
        }
        cfg = environ.to_config(Config, environ=env)

        assert cfg.postgres.data.database == "testdb"
        assert cfg.postgres.data.user == "postgres"
        assert cfg.postgres.data.port == 5432
        assert cfg.app.debug is False
        assert cfg.security.api_key == "secret-api-key"
        assert cfg.activity.max_depth == 3

    def test_database_url_property(self) -> None:
        env = {
            "APP_POSTGRES_DATA_DATABASE": "mydb",
            "APP_POSTGRES_DATA_USER": "user1",
            "APP_POSTGRES_DATA_PASSWORD": "pass1",
            "APP_POSTGRES_DATA_HOST": "localhost",
            "APP_POSTGRES_DATA_PORT": "5433",
        }
        cfg = environ.to_config(Config, environ=env)

        assert cfg.postgres.data.database_url == (
            "postgresql+asyncpg://user1:pass1@localhost:5433/mydb"
        )

    def test_debug_converter(self) -> None:
        env_true = {"APP_APP_DEBUG": "true"}
        cfg = environ.to_config(Config, environ=env_true)
        assert cfg.app.debug is True

        env_false = {"APP_APP_DEBUG": "false"}
        cfg = environ.to_config(Config, environ=env_false)
        assert cfg.app.debug is False

    def test_pool_settings(self) -> None:
        env = {
            "APP_POSTGRES_DATA_POOL_SIZE": "20",
            "APP_POSTGRES_DATA_POOL_MAX_OVERFLOW": "10",
            "APP_POSTGRES_DATA_POOL_RECYCLE": "600",
        }
        cfg = environ.to_config(Config, environ=env)

        assert cfg.postgres.data.pool_size == 20
        assert cfg.postgres.data.pool_max_overflow == 10
        assert cfg.postgres.data.pool_recycle == 600


class TestConfigToEnvDict:
    def test_converts_config_to_dict(self) -> None:
        cfg = environ.to_config(Config, environ={})
        result = config_to_env_dict(cfg)

        assert isinstance(result, dict)
        assert "APP_POSTGRES_DATA_DATABASE" in result
        assert "APP_APP_TITLE" in result
        assert "APP_SECURITY_API_KEY" in result
        assert "APP_ACTIVITY_MAX_DEPTH" in result
