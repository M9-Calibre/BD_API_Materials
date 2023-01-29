#!/bin/bash

rm -f db.sqlite3
rm -r API_Materials/migrations/
python3 manage.py makemigrations API_Materials
python3 manage.py migrate