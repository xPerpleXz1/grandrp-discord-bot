import os
import psycopg2
import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
c = conn.cursor()

# Tabelle erstellen
c.execute("""
CREATE TABLE IF NOT EXISTS artikel (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    preis REAL NOT NULL,
    zeit TIMESTAMP NOT NULL
)
""")
conn.commit()


def add_preis(artikel, preis):
    zeit = datetime.datetime.now()
    c.execute("INSERT INTO artikel (name, preis, zeit) VALUES (%s, %s, %s)",
              (artikel, preis, zeit))
    conn.commit()


def get_preise(artikel):
    c.execute("SELECT preis, zeit FROM artikel WHERE name=%s ORDER BY zeit", (artikel,))
    return c.fetchall()


def get_aktueller_preis():
    c.execute("""
        SELECT DISTINCT ON (name) name, preis 
        FROM artikel 
        ORDER BY name, zeit DESC
    """)
    return c.fetchall()
