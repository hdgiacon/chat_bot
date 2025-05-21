#!/bin/bash

if ! nc -z localhost 6379; then
    echo ">>----- Redis is not running, starting Redis Server -----<<"
    redis-server &
    sleep 5
fi

echo ">>----- Running Django Entry Point -----<<"
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:5000
