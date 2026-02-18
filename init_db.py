import sqlite3  # Make sure to import the sqlite3 module

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key support
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table if not exists, including the 'balance' column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            credit REAL DEFAULT 0,
            balance TEXT NOT NULL
           
                   
        )
    ''')

    # Create transactions table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            bank TEXT NOT NULL,
            account_number TEXT NOT NULL,
            amount REAL NOT NULL,
            coins REAL NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE  -- Added ON DELETE CASCADE
        )
    ''')

    # Create user_coins table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_coins (
            user_id INTEGER PRIMARY KEY,
            total_coins REAL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE  -- Added ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

# Initialize the database
init_db()  # Make sure to call this before inserting users
