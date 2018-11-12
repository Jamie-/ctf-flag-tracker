#!/bin/sh

# Check for database existence, create if required
python setupdb.py

exec $@
