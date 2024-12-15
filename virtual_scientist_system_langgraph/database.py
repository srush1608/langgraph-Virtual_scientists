import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

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

def create_table():
    """Creates the necessary table to store query and response data if it doesn't exist."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_chat_history (
            id SERIAL PRIMARY KEY,
            topic VARCHAR(255),          -- Name of the topic
            abstract TEXT,               -- Final generated abstract
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def store_query_response(topic, abstract):
    """Stores the query (topic) and the response (abstract) in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        INSERT INTO research_chat_history (topic, abstract)
        VALUES (%s, %s);
    """
    cursor.execute(query, (topic, abstract))
    conn.commit()
    cursor.close()
    conn.close()

create_table()
