.DEFAULT_GOAL := run
.PHONY: clean, clean-db, init, run

clean:
	rm -rf *.pyc
	rm -rf __pycache__/

clean-db:
	rm -rf *.db

init:
	python3 -c 'from tracker.db import init_db; init_db()'

run:
	./run.py
