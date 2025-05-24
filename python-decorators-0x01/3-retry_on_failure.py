import time
import sqlite3 
import functools

#### paste your with_db_decorator here
def with_db_connection(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		conn = sqlite3.connect('users.db')
		try:
			return func(conn, *args, **kwargs)
		finally:
			conn.close()
	return wrapper

def retry_on_failure(retries=3, delay=1):
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			attempts = 0
			while attempts < retries:
				try:
					return func(*args, **kwargs)
				except Exception as e:
					attempts += 1
					if attempts == retries:
						raise
						print(f"Attemp {attempts} failed with error: {e}. Retrying in {delay} seconds...")
						time.sleep(dely)
		return wrapper
	return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)