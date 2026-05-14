#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
# Retry migrate up to 5 times to handle Render Free Tier Postgres wake-up
n=0
until [ "$n" -ge 5 ]
do
   python manage.py migrate && break
   n=$((n+1))
   echo "Migration failed due to database wake-up. Retrying in 10 seconds... ($n/5)"
   sleep 10
done

# Run professional production setup
python manage.py setup_production
