.PHONY: run format

run:
	uv run ./cek-belum-ta.py

format:
	uvx isort ./cek-belum-ta.py
	uvx ruff format ./cek-belum-ta.py

