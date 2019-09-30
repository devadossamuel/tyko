#!/usr/bin/env bash

python -m tyko init-db
gunicorn --workers=5  --bind 0.0.0.0:8000  "tyko.run:create_app()"