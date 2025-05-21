#!/usr/bin/python3
import mysql.connector
from seed import connect_to_prodev

def stream_user_ages():
    connection = connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute("SELECT age FROM user_data")
    for row in cursor:
        yield row[0]
    cursor.close()
    connection.close()

def compute_average_age():
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1
    if count > 0:
        print(f"Average age of users: {total_age / count:.2f}")
    else:
        print("No users in database")

if __name__ == '__main__':
    compute_average_age()
