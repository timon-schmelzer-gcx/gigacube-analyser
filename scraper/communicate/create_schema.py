import os

from dbutils import create_connection
from dbutils import insert_data
from dbutils import read_schema
from dbutils import set_time_zone
from dbutils import EXAMPLE_DATA

INGEST_EXAMPLES = False

if __name__=='__main__':
    with create_connection() as con:
        # create tables
        cur = con.cursor()
        db_schema = read_schema()

        print(f'Creating new schema:\n\n{db_schema}\n')
        cur.execute(db_schema)

        con.commit()

        print('Setting correct time zone...')
        set_time_zone(con)
        con.commit()

        print('Done!')

        if INGEST_EXAMPLES:
            # add data
            for data_obj in EXAMPLE_DATA:
                insert_data(con, data_obj)

            # read data
            cur.execute(f'''SELECT * FROM {os.getenv('POSTGRES_SCHEMA')}.data''')
            print('DATA:', cur.fetchall())

            cur.execute(f'''SELECT * FROM {os.getenv('POSTGRES_SCHEMA')}.billing''')
            print('BILLING:', cur.fetchall())
