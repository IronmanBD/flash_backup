from __future__ import absolute_import, unicode_literals

from celery import Celery
import sqlalchemy as db
from models.opmob import OpmobModel
import redis
from datetime import timedelta

# Create Celery beat schedule:
celery_get_manifest_schedule = {
    'schedule-name': {
        'task': 'app.tasks.periodic_run_get_manifest',
        'schedule': timedelta(seconds=1200),
    },
}

CELERYBEAT_SCHEDULE = celery_get_manifest_schedule


def make_celery(app_name=__name__):
    broker_uri = 'redis://localhost'
    result_backend = 'db+postgresql://postgres:postgres@localhost:5432/da'
    return Celery(app_name, broker=broker_uri, backend=result_backend, include=['app.tasks'])

def make_client_db_connection():
    return db.create_engine('postgresql://postgres:postgres@122.102.35.226:5432/da')

def make_local_db_connection():
    return db.create_engine('postgresql://postgres:postgres@localhost:5432/da')

celery = make_celery()
client_db = make_client_db_connection()
local_db = make_local_db_connection()
default_schema = 'public'
models_of_tables_to_be_created = [OpmobModel]

