
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
	@python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@python3 -m flake8 .


# T1 D1-way1 D2-way1
# T2 D1-way3 D2-way3 D3-way1 D4-way1
# T3 D1-way5 D2-way5
# T4 D3-way3 D4-way3 D5-way1
# T5 D1-goal D2-goal D3-way5 D4-way5
# T6 D5-way3
# T7 D3-goal D4-goal D5-way5
# T8 D5-goal