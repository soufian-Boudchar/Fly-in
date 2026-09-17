
run:
	@python3 -m src map.txt

install:
	@pip install pygame
	@pip install mypy
	@pip install flake8
debug:
	@python3 -m pdb -m src

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
lint:
	@python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@python3 -m flake8 .
