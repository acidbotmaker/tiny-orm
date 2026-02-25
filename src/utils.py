import mysql.connector
from settings import db_settings
from typing import Optional
from mysql.connector.connection import MySQLConnection


def get_db_connection() -> Optional[MySQLConnection]:
    try:
        connection = mysql.connector.connect(
            host=db_settings.DB_HOST,
            user=db_settings.DB_USER,
            password=db_settings.DB_PASSWORD,
            database=db_settings.DB_NAME,
        )
        return connection

    except mysql.connector.Error as error:
        print(f"Failed to connect to database: {error}")
        return None
