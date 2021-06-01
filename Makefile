check:
	black --check .
	isort --check-only .
	flake8 .
	pylint dice_10001 tests
	mypy --strict --exclude 'main.py' .

test:
	coverage run --source=dice_10001 -m pytest -vvv
	coverage report -m --skip-covered --fail-under=100

.PHONY: check test
