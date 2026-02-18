import sqlite3

def insert_user(name, username, email, credit, password, balance):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # SQL query to insert a new user
    cursor.execute('''
        INSERT INTO users (name, username, email, credit, password, balance) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, username, email, credit, password, balance))

    conn.commit()
    conn.close()
    print(f"User '{username}' added successfully.")

# Example usage
if __name__ == "__main__":
    new_name = input("Enter the name: ")
    new_username = input("Enter the username: ")
    new_email = input("Enter the email: ")
    new_password = input("Enter the password: ")
    new_credit = float(input("Enter the credit amount: "))
    
    new_balance = input("Allocate card Number: ")

    insert_user(new_name, new_username, new_email, new_credit, new_password, new_balance)
