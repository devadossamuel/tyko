#!/usr/bin/env bash

#echo "Initalizing database"
#python -m tyko init-db
echo "Starting Tyko"
gunicorn --workers=5  --bind 0.0.0.0:8000  "tyko.run:create_app()"