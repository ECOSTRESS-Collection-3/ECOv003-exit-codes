PACKAGE_NAME = ECOv003-exit-codes

.PHONY: clean test build twine-upload dist install uninstall reinstall repomix

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

test:
	pytest

build:
	python -m build

twine-upload:
	twine upload dist/*

dist: clean build twine-upload

install:
	pip install -e ".[dev]"

uninstall:
	pip uninstall -y $(PACKAGE_NAME)

reinstall: uninstall install

repomix:
	npx repomix