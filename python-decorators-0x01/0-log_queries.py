import sqlite3
import functools

#### decorator to lof SQL queries

def log_queries(fetch_all_users):
	@functools.wraps(fetch_all_users)
	def wrapper(*args, **kwargs):
		# Check if query is passed positionally or as a keyword
		if args:
			query = args[0]
		elif 'query' in kwargs:
			query = kwargs['query']
		else:
			query = "<NO QUERY FOUND>"
		print(f"SQL Query: {query}")
		return fetch_all_users(*args, **kwargs)
	return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")