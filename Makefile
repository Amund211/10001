check:
	black --check .
	isort --check-only .
	flake8 .
	pylint dice_10001 tests

.PHONY: check
