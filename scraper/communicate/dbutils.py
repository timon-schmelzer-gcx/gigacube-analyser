import datetime
import typing
import os

import psycopg2
import dotenv

dotenv.load_dotenv()

def create_connection() -> psycopg2.connect:
    '''Creates a connection to the postgres database.'''
    return psycopg2.connect(host=os.getenv('POSTGRES_HOST'),
                            user=os.getenv('POSTGRES_USER'),
                            password=os.getenv('POSTGRES_PASSWORD'),
                            dbname=os.getenv('POSTGRES_DB'))

def read_schema(path: str='communicate/schemas/gigacube.sql') -> str:
    '''Read file and returns output as string.'''
    with open(path, 'r') as infile:
        content = infile.read()
    return content

def set_time_zone(con: psycopg2):
    '''Sets the correct time zone to postgres.'''
    with con.cursor() as cur:
        cur.execute(f"SET TIMEZONE='UTC';")

def create_schema(get_schema: typing.Callable[[typing.Any], str]=read_schema,
                  get_connection: typing.Callable[
                      [typing.Any], psycopg2.connect]=create_connection):
    schema = get_schema()
    with get_connection() as con:
        cur = con.cursor()
        cur.execute(schema)

        con.commit()

def hash_md5(identifier: str):
    '''Returns MD5 hash from given string.'''
    import hashlib

    return hashlib.md5(identifier.encode()).hexdigest()

DATA_TEMPLATE = f'''--sql-begin
    INSERT INTO {os.getenv('POSTGRES_SCHEMA')}.data
    (timestamp, volume, billing_id)
    VALUES (%s, %s, %s);
'''

BILLING_TEMPLATE = f'''--sql-begin
    INSERT INTO {os.getenv('POSTGRES_SCHEMA')}.billing
    (billing_id, start_date, end_date, total_volume)
    VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;
'''

def insert_data(con: psycopg2.connect,
                data_obj: typing.Dict[str, typing.Any],
                hash_func: typing.Callable[[str], str]=hash_md5,
                data_template: str=DATA_TEMPLATE,
                billing_template: str=BILLING_TEMPLATE) -> None:
    '''Insert data object into database.

    data_obj must be in the following format:
        {
            "current_volume": 186.209,
            "total_volume": 500.0,
            "start_date": "2021-10-05 00:00:00",
            "end_date": "2021-11-04 00:00:00",
            "timestamp": "2021-10-18 17:04:06"
        }
    '''
    cur = con.cursor()

    billing_id = hash_func(data_obj['start_date'] +
                           data_obj['end_date'] +
                           str(data_obj['total_volume']))
    cur.execute(data_template,
                (data_obj['timestamp'],
                 data_obj['current_volume'],
                 billing_id))
    cur.execute(billing_template,
                (billing_id,
                 data_obj['start_date'],
                 data_obj['end_date'],
                 data_obj['total_volume']))

    con.commit()



EXAMPLE_DATA = [
    {"current_volume": 186.209, "total_volume": 500.0, "start_date": "2021-10-05 00:00:00", "end_date": "2021-11-04 00:00:00", "timestamp": "2021-10-18 17:04:06"},
    {"current_volume": 186.209, "total_volume": 500.0, "start_date": "2021-10-05 00:00:00", "end_date": "2021-11-04 00:00:00", "timestamp": "2021-10-18 17:05:06"},
    {"current_volume": 186.209, "total_volume": 500.0, "start_date": "2021-10-05 00:00:00", "end_date": "2021-11-04 00:00:00", "timestamp": "2021-10-18 17:06:05"},
    {"current_volume": 186.209, "total_volume": 500.0, "start_date": "2021-10-05 00:00:00", "end_date": "2021-11-04 00:00:00", "timestamp": "2021-10-18 17:07:06"},
    {"current_volume": 186.287, "total_volume": 500.0, "start_date": "2021-10-05 00:00:00", "end_date": "2021-11-04 00:00:00", "timestamp": "2021-10-18 17:08:06"}
]
