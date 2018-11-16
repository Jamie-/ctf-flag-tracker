#!/bin/sh

# Check for database existence, create if required
python setupapp.py

exec $@
