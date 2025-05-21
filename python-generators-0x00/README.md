# Python Generators - Task 0

## Objective

Set up a MySQL database and stream rows using Python.

## Files

- `seed.py`: Python script to set up the `ALX_prodev` MySQL database, create the `user_data` table, and populate it from a CSV.
- `user_data.csv`: Sample user data with the following columns:
  - `user_id` (UUID)
  - `name`
  - `email`
  - `age`

## Functions

### `connect_db()`
Connects to MySQL server (not to a specific database yet).

### `create_database(connection)`
Creates the `ALX_prodev` database if it doesn't exist.

### `connect_to_prodev()`
Connects to the `ALX_prodev` database.

### `create_table(connection)`
Creates the `user_data` table with the following columns:
- `user_id`: Primary Key, UUID
- `name`: NOT NULL
- `email`: NOT NULL
- `age`: NOT NULL

Also creates an index on `user_id`.

### `insert_data(connection, filename)`
Reads user data from `user_data.csv` and inserts into the `user_data` table if it doesn't already exist.

## Execution

Run the script via the provided `0-main.py`.

### Sample Output

```bash
$ ./0-main.py
connection successful
Table user_data created successfully
Database ALX_prodev is present 
[('uuid1', 'John Doe', 'john@example.com', 32), ...]
