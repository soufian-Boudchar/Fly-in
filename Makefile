
run:
	@python3 -m src maps/easy/01_linear_path.txt

install:
	@pip install pygame
debug:
	@python3 -m pdb -m src

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
lint:
	@uv run -m mypy src/*py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@uv run -m flake8 src/**