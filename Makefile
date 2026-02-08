PROJECT := src
TESTS := tests
REPORTS := .reports
COVERAGE := $(REPORTS)/coverage

clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf $(REPORTS)

install-deps:
	uv sync
	uv sync --group dev

$(REPORTS):
	mkdir -p $(REPORTS)

setup: $(REPORTS)

ruff-format: setup
	uv run ruff format $(PROJECT) $(TESTS)

ruff-format-check: setup
	uv run ruff format --check $(PROJECT) $(TESTS)

ruff-lint: setup
	uv run ruff check $(PROJECT) $(TESTS) --fix-only

ruff-lint-check: setup
	uv run ruff check $(PROJECT) $(TESTS)

test: setup
	uv run coverage erase
	uv run pytest $(TESTS) \
		--cov $(PROJECT) \
		--cov-config pyproject.toml \
		--cov-report term-missing \
		--cov-append \
		--no-cov-on-fail \
		--junitxml=$(REPORTS)/junit.xml
	uv run coverage html -d $(COVERAGE)/html
	uv run coverage xml -o $(COVERAGE)/cobertura.xml

format: ruff-format ruff-lint

lint: ruff-lint-check ruff-format-check

sure: format lint

build:
	docker compose build

run:
	docker compose up -d
stop:
	docker compose stop

down:
	docker compose down

logs:
	docker compose logs -f

refresh: down run logs

all: format lint test build

.DEFAULT_GOAL := all
.PHONY: clean install-deps setup ruff-format ruff-format-check ruff-lint ruff-lint-check test format lint sure build run stop all
