import psycopg2
from psycopg2 import sql
from utils.read_params import read_params
from dotenv import load_dotenv
import os

params = read_params()

load_dotenv()
# Database connection details
RDS_HOST = os.getenv('RDS_HOST')
RDS_PORT = params['RDS_PORT']
RDS_NAME = params['RDS_NAME']
RDS_USER = os.getenv('RDS_USER')
RDS_PASSWORD = os.getenv('SkandIsmaBadrX17')

print(RDS_HOST)
print(RDS_PORT)
print(RDS_NAME)
print(RDS_USER)
print(RDS_PASSWORD)

# Connect to the PostgreSQL database
try:
    conn = psycopg2.connect(
        dbname=RDS_NAME,
        user=RDS_USER,
        password=RDS_PASSWORD,
        host=RDS_HOST,
        port=RDS_PORT
    )
    print("Connection to PostgreSQL DB successful")
except Exception as e:
    print(f"Error: {e}")
    exit()

# # Create a cursor object
# cur = conn.cursor()

# # Create a table
# create_table_query = '''
# CREATE TABLE IF NOT EXISTS test_table (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(100),
#     age INT
# )
# '''
# try:
#     cur.execute(create_table_query)
#     conn.commit()
#     print("Table created successfully")
# except Exception as e:
#     print(f"Error creating table: {e}")
#     conn.rollback()

# # Insert a row into the table
# insert_query = '''
# INSERT INTO test_table (name, age) VALUES (%s, %s)
# RETURNING id
# '''
# try:
#     cur.execute(insert_query, ('John Doe', 30))
#     inserted_id = cur.fetchone()[0]
#     conn.commit()
#     print(f"Row inserted successfully with id {inserted_id}")
# except Exception as e:
#     print(f"Error inserting row: {e}")
#     conn.rollback()

# # Close the cursor and connection
# cur.close()
conn.close()
