# Organization Directory API

## Стек технологий

- **Python 3.13**, **FastAPI**, **Pydantic v2**
- **SQLAlchemy 2.0** + **asyncpg**
- **PostgreSQL 16** + **PostGIS 3.4**
- **GeoAlchemy2** + **Shapely**
- **Alembic** (миграции)
- **Docker Compose**

## Структура проекта

```
src/
  api/
    v1/              # Обработчики  (buildings, organizations)
    dependencies/    # FastAPI DI (сервисы, авторизация, БД)
    middleware/       # Обработчики исключений
  core/              # Конфигурация
  domain/
    models/          # SQLAlchemy ORM модели
    schemas/         # Pydantic схемы
    interfaces/      # Протоколы репозиториев
    exceptions/      # Доменные исключения
  infrastructure/
    repositories/    # Реализации репозиториев
  services/          # Бизнес-логика
  seed.py            # Скрипт заполнения БД тестовыми данными
migrations/          # Alembic миграции
tests/
  unit/              # Юнит-тесты (сервисы, конфигурация, исключения)
  integration/       # Интеграционные тесты (API эндпоинты)
```

## Быстрый старт

### Docker Compose

```bash
make build   # Сборка Docker-образов
make run     # Запуск PostgreSQL + API (применяет миграции, заполняет БД)
```

API будет доступен по адресу `http://localhost:8000`.

### Локальная разработка

Требования: Python 3.13+, [uv](https://docs.astral.sh/uv/), запущенный PostgreSQL с PostGIS.

```bash
# Установка зависимостей
make install-deps

# Настройка переменных окружения (скопировать и отредактировать)
cp .env.example .env

# Применение миграций
uv run alembic upgrade head

# Заполнение БД тестовыми данными
uv run python -m src.seed

# Запуск сервера
uv run uvicorn src.main:app --reload
```

## Переменные окружения

Все переменные используют префикс `APP_`. Значения по умолчанию подходят для локальной разработки с Docker Compose.

### База данных (`APP_POSTGRES_DATA_*`)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `APP_POSTGRES_DATA_DATABASE` | `directory` | Имя базы данных |
| `APP_POSTGRES_DATA_HOST` | `127.0.0.1` | Хост PostgreSQL |
| `APP_POSTGRES_DATA_PORT` | `5432` | Порт PostgreSQL |
| `APP_POSTGRES_DATA_USER` | `postgres` | Пользователь БД |
| `APP_POSTGRES_DATA_PASSWORD` | `postgres` | Пароль БД |
| `APP_POSTGRES_DATA_POOL_SIZE` | `5` | Размер пула соединений |
| `APP_POSTGRES_DATA_POOL_MAX_OVERFLOW` | `2` | Макс. дополнительных соединений |
| `APP_POSTGRES_DATA_POOL_RECYCLE` | `1200` | Время переиспользования соединения (сек) |

### Приложение (`APP_APP_*`)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `APP_APP_TITLE` | `Organization Directory API` | Название приложения (Swagger UI) |
| `APP_APP_VERSION` | `1.0.0` | Версия приложения |
| `APP_APP_DEBUG` | `false` | Режим отладки (`true`/`false`) |

### Безопасность (`APP_SECURITY_*`)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `APP_SECURITY_API_KEY` | `secret-api-key` | API-ключ для аутентификации |

Все эндпоинты требуют заголовок `X-Api-Key`:

```bash
curl -H "X-Api-Key: secret-api-key" http://localhost:8000/api/v1/buildings/
```

### Настройки видов деятельности (`APP_ACTIVITY_*`)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `APP_ACTIVITY_MAX_DEPTH` | `3` | Максимальная глубина вложенности видов деятельности |

## Документация API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Команды Makefile

| Команда | Описание |
|---|---|
| `make install-deps` | Установка всех зависимостей (включая dev) |
| `make format` | Автоформатирование кода (ruff format + сортировка импортов) |
| `make lint` | Проверка линтером |
| `make sure` | Форматирование + линтер |
| `make test` | Запуск тестов с покрытием |
| `make build` | Сборка Docker-образов |
| `make run` | Запуск Docker Compose |
| `make stop` | Остановка Docker Compose |
| `make down` | Остановка и удаление контейнеров + томов |
| `make logs` | Просмотр логов Docker Compose |
| `make all` | Форматирование + линтер + тесты + сборка |

## Тестирование

```bash
make test
```

Запускает pytest с отчётом о покрытии. Минимальный порог покрытия: 70%.
