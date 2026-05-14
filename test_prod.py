import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_food.settings')
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'

django.setup()

from django.test import Client
c = Client()
try:
    response = c.get('/')
    print("STATUS:", response.status_code)
except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()
