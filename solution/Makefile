up:
	sudo docker compose up --build
test:
	sudo docker compose -f docker-compose.test.yml up --build
unit:
	pytest tests/unit
down:
	sudo docker compose down
	sudo docker compose -f docker-compose.test.yml down
lint:
	ruff format
	mypy --no-incremental
	ruff check --fix