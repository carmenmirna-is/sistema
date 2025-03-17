import psycopg2
from psycopg2 import sql

def get_db_connection():
    conn = psycopg2.connect(
        dbname="sistema_web",
        user="postgres",
        password="123456789",
        host="localhost",
        port="5432"
    )
    return conn