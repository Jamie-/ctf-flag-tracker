.DEFAULT_GOAL := run
.PHONY: clean, clean-db, setup, depends

clean: # Clean build files
	rm -rf **/*.pyc
	rm -rf **/__pycache__/

clean-db: # Delete database
	rm -rf *.db

setup: # Setup virtual environment
	python3 -m venv venv

depends:
	venv/bin/pip3 install -r requirements.txt
