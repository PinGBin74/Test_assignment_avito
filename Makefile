.PHONY: run down lint migrate test db-up dev

run:
	docker-compose up --build

down:
	docker-compose down

lint:
	ruff check .

migrate:
	alembic upgrade head

test:
	poetry run pytest -v



