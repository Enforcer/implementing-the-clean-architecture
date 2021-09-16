
.PHONY: lint
lint:
	isort itca tests
	black itca tests
	flake8 itca tests
	mypy --ignore-missing-imports itca tests
