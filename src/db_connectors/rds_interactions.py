import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import logging
from utils.read_params import read_params

def connect_to_db(dbname, user, password, host, port):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        logging.info("Connection to PostgreSQL DB successful")
        return conn
    except psycopg2.Error as e:
        logging.info(f"Error: Could not connect to PostgreSQL\n{e}")
        raise  # Re-raise the exception to propagate it further

def read_db_params():
    # Example function to read database parameters from configuration file or environment variables
    load_dotenv()
    params = read_params()
    RDS_HOST = os.getenv('RDS_HOST')
    RDS_PORT = params['rds']['RDS_PORT']
    RDS_NAME = params['rds']['RDS_NAME']
    RDS_USER = os.getenv('RDS_USER')
    RDS_PASSWORD = os.getenv('RDS_PASSWORD')
    return RDS_NAME, RDS_USER, RDS_PASSWORD, RDS_HOST, RDS_PORT

def insert_to_table(conn, table_name, data_to_insert):
    cur = conn.cursor()

    columns = data_to_insert.keys()

    insert_query = sql.SQL("""
        INSERT INTO {} ({})
        VALUES ({})
    """).format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(', ').join(map(sql.Placeholder, columns))
    )

    try:
        cur.execute(insert_query, data_to_insert)
        conn.commit()
        logging.info("Row inserted successfully")
    except Exception as e:
        logging.info(f"Error inserting row: {e}")
        conn.rollback()
    finally:
        cur.close()


# dbname, user, password, host, port = read_db_params()
# conn = connect_to_db(dbname, user, password, host, port)

# Example usage:
# data_to_insert = {
#     'call_sid': '12345',
#     'datetime': '2024-06-12 15:30:00',
#     'prenom': 'John',
#     'nom': 'Doe',
#     'telephone': '123-456-7890',
#     'description': 'Example description',
#     'immatriculation': 'ABC123',
#     'marque': 'Toyota',
#     'modele': 'Camry'
# }



# Create a cursor object
# cur = conn.cursor()

# # Create a table
# create_table_query = '''
# CREATE TABLE IF NOT EXISTS requests_table (
#     call_sid VARCHAR(100) PRIMARY KEY,
#     datetime VARCHAR(100),
#     prenom VARCHAR(100),
#     nom VARCHAR(100),
#     telephone VARCHAR(100),
#     description TEXT,
#     immatriculation VARCHAR(100),
#     marque VARCHAR(100),
#     modele VARCHAR(100)
# )
# '''
# try:
#     cur.execute(create_table_query)
#     conn.commit()
#     logging.info("Table created successfully")
# except Exception as e:
#     logging.info(f"Error creating table: {e}")
#     conn.rollback()

# Data to insert
# data_to_insert = {
#     'prenom': 'Jean',
#     'nom': 'Prié',
#     'telephone': '0613401340',
#     'description': 'Problème de frein et pneus',
#     'immatriculation': '1452FA94',
#     'marque': 'Ford',
#     'modele': 'Fiesta',
#     'datetime': '2024-06-12_13-29-08',
#     'call_sid': 'CAb01b1f16c88d2de084b947a5a5643d67'
# }

