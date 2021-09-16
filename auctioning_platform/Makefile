
.PHONY: lint
lint:
	isort itca tests
	black itca tests
	flake8 itca tests
	mypy --ignore-missing-imports itca tests

.PHONY: check
check:
	isort --check itca tests
	black --check itca tests
	flake8 itca tests
	mypy --ignore-missing-imports itca tests

