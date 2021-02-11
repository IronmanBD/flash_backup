from __future__ import absolute_import, unicode_literals

from app import celery
from app import client_db, local_db, default_schema, models_of_tables_to_be_created
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import traceback
from models.opmob import OpmobModel
from datetime import timedelta
from celery.exceptions import MaxRetriesExceededError

from celery.signals import celeryd_init, worker_process_init
from celery.task.base import periodic_task
from sqlalchemy import and_, or_
import requests
import json
import datetime

@celeryd_init.connect
def create_tables_to_client_db_at_startup(conf=None, **kwargs):
    print("Creating All Tables")
    for model in models_of_tables_to_be_created:
        try:
            if not client_db.has_table(model.__tablename__, schema = default_schema):
                print(f"Table {model.__tablename__} not found in DB. Creating...")
                model.__table__.create(client_db)
                print(f"Table {model.__tablename__} created")
            else:
                print(f"Table {model.__tablename__} already exists in DB")
        except Exception:
            traceback.print_exc()


@celery.task()
def add_single_row_to_client_db_by_celery(table_name, json_object):
    try:
        connection = client_db.connect()
        metadata = db.MetaData()
        users = db.Table(table_name, metadata, autoload=True, autoload_with=client_db)
        query = db.insert(users)
        values = [json_object]
        ResultProxy = connection.execute(query, values)
    except Exception:
        traceback.print_exc()


@celery.task(max_retries = 5, default_retry_delay=10)
def add(a, b):
    try:
        raise Exception
    except Exception:
        try:
            add.retry()
        except MaxRetriesExceededError:
                print("Max Retries Failed")


@celery.task()
def add_all_rows_to_client_db_by_celery(table_name, json_list):
    try:
        connection = client_db.connect()
        metadata = db.MetaData()
        users = db.Table(table_name, metadata, autoload=True, autoload_with=client_db)
        query = db.insert(users)
        values = json_list
        ResultProxy = connection.execute(query, values)
    except Exception:
        traceback.print_exc()


@celery.task()
def delete_from_client_db_with_custom_key_by_celery(table_name, delete_key_value_pair_list):
    connection = client_db.connect()
    metadata = db.MetaData()
    table = db.Table(table_name, metadata, autoload=True, autoload_with=client_db)
    delete_filter_list = []
    for key, value in delete_key_value_pair_list:
        delete_filter_list.append(table.c[key] == value)
    query = table.delete().where(and_(*delete_filter_list))
    try:
        ResultProxy = connection.execute(query)
        print(f"Deleted {ResultProxy.rowcount} rows")
    except:
        print("Delete Failed")
        traceback.print_exc()


@celery.task()
def delete_from_client_db_with_primary_key_by_celery(table_name, json_object):
    connection = client_db.connect()
    metadata = db.MetaData()
    table = db.Table(table_name, metadata, autoload=True, autoload_with=client_db)
    delete_filter_list = []
    for key in table.primary_key.columns.keys():
        delete_filter_list.append(table.c[key] == json_object[key])
    query = table.delete().where(and_(*delete_filter_list))
    try:
        ResultProxy = connection.execute(query)
        print(f"Deleted {ResultProxy.rowcount} rows")
    except:
        print("Delete Failed")
        traceback.print_exc()


@celery.task()
def update_client_db_with_custom_key_by_celery(table_name, json_object, update_key_value_pair_list):
    connection = client_db.connect()
    metadata = db.MetaData()
    table = db.Table(table_name, metadata, autoload=True, autoload_with=client_db)
    update_filter_list = []
    for key, value in update_filter_list:
        update_filter_list.append(table.c[key] == value)
    query = table.update().values(json_object).where(and_(*update_filter_list))
    try:
        ResultProxy = connection.execute(query)
        print(f"Updated {ResultProxy.rowcount} rows")
    except:
        print("Update Failed")
        traceback.print_exc()


@celery.task()
def update_client_db_with_primary_key_by_celery(table_name, json_object):
    connection = client_db.connect()
    metadata = db.MetaData()
    table = db.Table(table_name, metadata, autoload=True, autoload_with=client_db)
    update_filter_list = []
    for key in table.primary_key.columns.keys():
        update_filter_list.append(table.c[key] == json_object[key])
    query = table.update().values(json_object).where(and_(*update_filter_list))
    try:
        ResultProxy = connection.execute(query)
        print(f"Updated {ResultProxy.rowcount} rows")
    except:
        print("Update Failed")
        traceback.print_exc()


@celery.task()
def receive_from_client_db(table_name, column_list, row_count_in_local = None):
    print("Receiveing From :", table_name)
    connection = client_db.connect()
    metadata = db.MetaData()
    table = db.Table(table_name, metadata, autoload=True, autoload_with=client_db)
    query = db.select([table])
    ResultProxy = connection.execute(query)
    print(f"Found {ResultProxy.rowcount} rows from table {table_name}")
    if row_count_in_local is not None:
        if ResultProxy.rowcount == row_count_in_local:
            return
   
    row_dict, data_list = {}, []
    for rowproxy in ResultProxy:
        for column, value in rowproxy.items():
            # build up the dictionary
            if column in column_list:
                row_dict = {**row_dict, **{column: value}}
        data_list.append(row_dict)
    
    Session = sessionmaker(bind=local_db, autocommit=False)
    session = Session()
    try:
        metadata = db.MetaData()
        table = db.Table(table_name, metadata, autoload=True, autoload_with=local_db)
        ResultProxy = session.execute(table.delete().where(True))
        print(f"{ResultProxy.rowcount} rows deleted from local DB of table {table_name} Successfully")
        ResultProxy = session.execute(db.insert(table), data_list)
        print(f"{ResultProxy.rowcount} rows inserted from remote DB of table {table_name} Successfully")
        session.commit()
    except Exception as ex:
        session.rollback()
        print(ex)
        print("Somethings Wrong. Rolling Back..")
    finally:
        print("Done")
        session.close()


@periodic_task(run_every=timedelta(seconds=1200))
def periodic_run_get_manifest():
    connection = local_db.connect()
    query = "DELETE FROM weather WHERE country = 'BD'"
    try:
        connection.execute(query)
    except Exception as err:
        print(err)

    api_key = "041b63b60b6d506b28245e3ad4fdafc4"
    location_list = ['Chittagong','Dhaka','Rajshahi','Sylhet','Mymensingh','Comilla','Barisal','Jessore','Brahmanbaria','Bogra','Rangpur','Dinajpur','Gazipur','Savar']
    country = 'BD'

    for i in location_list:
        try:
            weather = WeatherModel.find_by_country_city(i,country)
        except Exception as err:
            weather = 0
        if weather:
            weather.delete_from_db()

    for i in location_list:
        url = "http://api.openweathermap.org/data/2.5/weather?q=%s,%s&APPID=%s" % (i, country, api_key)
        response = requests.get(url)
        data = json.loads(response.text)

        ztime = datetime.datetime.now()
        ztime = ztime.strftime('%m/%d/%YT%H:%M:%S')
        short_desc = data['weather'][0]['main']
        full_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        pressure = data['main']['pressure']
        humidity = data['main']['humidity']
        name = data['name']
 

        metadata = db.MetaData()
        query = "INSERT INTO weather (ztime,short_desc,full_desc,temp,feels_like,pressure,humidity,country,name) VALUES ('%s','%s','%s',%s,%s,%s,%s,'%s','%s')" % (ztime,short_desc,full_desc,temp,feels_like,pressure,humidity,country,name)
        connection.execute(query)
        print('query connection completed')
    return {'message':'All weather data has been succesfully inserted into the database table'}




