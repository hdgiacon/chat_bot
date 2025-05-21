import os
import sys
import django
from decouple import config

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_bot_api.settings')

django.setup()

from user.models import CustomUser


if not CustomUser.objects.filter(email = config('DB_USER') + '@test.com').exists():
    CustomUser.objects.create_superuser(
        first_name = config('DB_USER'),
        last_name = 'test',
        email = f"{config('DB_USER')}@test.com",
        password = config('DB_PASSWORD')
    )
    print("Superusuário criado.")

else:
    print("Superusuário já existe.")