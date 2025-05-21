#!/bin/bash

wait-for-it $DB_HOST:$DB_PORT -t 0

if [[ "$LOCAL_ENTRYPOINT" == "True" ]]; then
    echo ">>----- Making migrations -----<<"
    python manage.py makemigrations

    echo ">>----- Migrate -----<<"
    python manage.py migrate

    echo ">>----- Creating super user -----<<"
    python manage.py shell <scripts/create_user.py
fi

echo ">>----- Starting server -----<<"
bash /app/scripts/celery_entrypoint.sh &
bash /app/scripts/django_entrypoint.sh
