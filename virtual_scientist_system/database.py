# import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

import psycopg2
from psycopg2 import sql

def connect_db():
    """Establishes a connection to PostgreSQL."""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"), 
        user=os.getenv("DB_USER"), 
        password=os.getenv("DB_PASS"), 
        host=os.getenv("DB_HOST"), 
        port=os.getenv("DB_PORT")
    )
    return conn

def store_query_response(agent, topic, response):
    """Stores query and response in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    query = sql.SQL("""
        INSERT INTO agent_responses (agent_name, topic, response)
        VALUES (%s, %s, %s);
    """)
    cursor.execute(query, (agent, topic, response))
    conn.commit()
    cursor.close()
    conn.close()

def create_table():
    """Creates the necessary table to store query and response data."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_responses (
            id SERIAL PRIMARY KEY,
            agent_name VARCHAR(255),
            topic VARCHAR(255),
            response TEXT
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
