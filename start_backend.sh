#!/bin/bash

if [ "$ENV" = "dev" ]; then
    echo "Running in development mode..."
    python3 -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m watchgod manage.py runserver 0.0.0.0:8000
else
    echo "Running in production mode..."
    daphne -b 0.0.0.0 -p 8000 LIVE_TRADER.asgi:application
fi
