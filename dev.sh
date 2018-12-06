#!/usr/bin/env bash

./venv/bin/gunicorn -b localhost:8080 -w 3 tracker:app --reload
