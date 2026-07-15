.PHONY: up test

up:
	PYTHONPATH=. poetry run python db/init_db.py
	PYTHONPATH=. poetry run uvicorn source.app:app --reload

test:
	poetry run python -m pytest test/unit/ -v
