#!/usr/bin/python3
import mysql.connector
from mysql.connector import Error
import csv
import uuid


def connect_db():
    """Connect to MySQL server (no specific database yet)."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_mysql_password"
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def create_database(connection):
    """Create ALX_prodev database if not exists."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """Connect to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_mysql_password",
            database="ALX_prodev"
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def create_table(connection):
    """Create user_data table with the required schema."""
    try:
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON user_data(user_id);")
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, filename):
    """Insert data from CSV file into user_data table."""
    try:
        cursor = connection.cursor()
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_id = row['user_id']
                cursor.execute("SELECT user_id FROM user_data WHERE user_id = %s", (user_id,))
                if cursor.fetchone():
                    continue  # Skip if already exists

                cursor.execute("""
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, row['name'], row['email'], row['age']))
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error inserting data: {e}")
    except FileNotFoundError:
        print("CSV file not found.")
