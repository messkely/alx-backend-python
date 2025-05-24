import time
import sqlite3 
import functools


query_cache = {}

def with_db_connection(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		conn = sqlite3.connect('users.db')
		try:
			return func(conn, *args, **kwargs)
		finally:
			conn.close()
	return wrapper

def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Try to extract the query string from args or kwargs
        query = None

        # If passed as positional (args), assume it's the first one after conn
        if len(args) > 0:
            query = args[0]
        # Or if passed as keyword argument
        elif 'query' in kwargs:
            query = kwargs['query']

        # Cache lookup
        if query in query_cache:
            print("Returning result from cache.")
            return query_cache[query]

        # If not cached, run the function and cache the result
        result = func(conn, *args, **kwargs)
        query_cache[query] = result
        return result

    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")