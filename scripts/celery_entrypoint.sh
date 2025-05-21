#!/bin/bash

echo ">>----- Starting Celery Worker -----<<"
celery -A cml_api worker -l INFO -c 1
