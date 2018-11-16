.PHONY: clean, setup, depends

clean: # Clean build files
	rm -rf **/*.pyc
	rm -rf **/__pycache__/

setup: # Setup virtual environment
	python3 -m venv venv

depends:
	venv/bin/pip3 install -r requirements.txt
