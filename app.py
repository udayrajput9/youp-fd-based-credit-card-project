from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Allows us to access columns by name
    return conn

# Database initialization
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        credit REAL DEFAULT 0)''')
    
    # Create transactions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        bank TEXT NOT NULL,
                        account_number TEXT NOT NULL,
                        amount REAL NOT NULL,
                        coins REAL NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

    # Create user_coins table
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_coins (
                        user_id INTEGER PRIMARY KEY,
                        total_coins REAL DEFAULT 0,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Home page route
@app.route('/')
def home():
    return render_template('home.html')

# Sign-up page route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        aadhar = request.form['aadhar']
        fd = request.form['fd']
        pan = request.form['pan']
        mobile = request.form['mobile']

        # Save the user data in a text file (not recommended for production)
        with open('user_details.txt', 'a') as file:
            file.write(f"Username: {username}, Email: {email}, FD: {fd},"
                       f"Aadhar: {aadhar}, PAN: {pan}, Mobile: {mobile}\n")


    return render_template('signup.html')

# Submission confirmation page route
@app.route('/submission_confirmation')
def submission_confirmation():
    return render_template('submission_confirmation.html')

# Sign-in page route
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Welcome, ' + user['username'], 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect email or password. Please try again.', 'danger')
    
    return render_template('signin.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('signin'))

    # Fetch user details from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()

    # Get the total coin balance for the logged-in user
    cursor.execute('SELECT total_coins FROM user_coins WHERE user_id = ?', (session['user_id'],))
    coin_row = cursor.fetchone()  # Fetch the row from user_coins table
    
    # Check if the user has a total_coins record
    total_coins = coin_row['total_coins'] if coin_row else 0  # Default value if no coins record exists

    conn.close()

    return render_template('dashboard.html', user=user, total_coins=total_coins)

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('signin'))

    # Fetch total coins for the logged-in user
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT total_coins FROM user_coins WHERE user_id = ?', (session['user_id'],))
    total_coins_row = cursor.fetchone()
    
    # Check if total coins exist and set to 0 if not found
    total_coins = total_coins_row['total_coins'] if total_coins_row else 0

    if request.method == 'POST':
        name = request.form['name']
        bank = request.form['bank']
        account_number = request.form['account_number']
        amount = float(request.form['amount'])

        # Fetch the user balance
        cursor.execute('SELECT credit FROM users WHERE id = ?', (session['user_id'],))
        user_balance = cursor.fetchone()['credit']

        # Check if the balance is sufficient
        if amount > user_balance:
            flash('Insufficient balance. Please wait for next month.', 'danger')
            return redirect(url_for('transaction'))

        # Process the transaction
        new_balance = user_balance - amount
        coins_earned = amount * 0.05  # Calculate coins earned (5%)
        
        # Update user balance and total coins
        cursor.execute('UPDATE users SET credit = ? WHERE id = ?', (new_balance, session['user_id']))
        cursor.execute('UPDATE user_coins SET total_coins = total_coins + ? WHERE user_id = ?', (coins_earned, session['user_id']))
        
        # Record the transaction
        cursor.execute('INSERT INTO transactions (user_id, name, bank, account_number, amount, coins) VALUES (?, ?, ?, ?, ?, ?)',
                       (session['user_id'], name, bank, account_number, amount, coins_earned))
        conn.commit()

        flash('Transaction processed successfully!', 'success')
        return redirect(url_for('dashboard'))

    # Fetch transaction history for the logged-in user
    cursor.execute('SELECT name, bank, account_number, amount, coins FROM transactions WHERE user_id = ?', (session['user_id'],))
    transactions = cursor.fetchall()

    # Ensure the fetched transactions are in a dictionary-like format
    transactions = [
        {
            'recipient_name': transaction['name'],
            'bank_name': transaction['bank'],
            'account_number': transaction['account_number'],
            'amount': transaction['amount'],
            'coins_earned': transaction['coins']
        }
        for transaction in transactions
    ]

    # Render the transaction page, ensuring total_coins and transactions are passed to the template
    return render_template('transaction.html', total_coins=total_coins, transactions=transactions)

@app.route('/redeem', methods=['POST'])
def redeem():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('signin'))

    # Fetch total coins for the logged-in user
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT total_coins FROM user_coins WHERE user_id = ?', (session['user_id'],))
    total_coins_row = cursor.fetchone()

    # Set total_coins to 0 if no record found
    total_coins = total_coins_row[0] if total_coins_row else 0

    # Check if the user has enough coins to redeem
    if total_coins >= 500:
        # Deduct coins and process redemption
        new_total_coins = total_coins - 500
        cursor.execute('UPDATE user_coins SET total_coins = ? WHERE user_id = ?', (new_total_coins, session['user_id']))
        conn.commit()

        flash('You have successfully redeemed 500 coins!', 'success')
    else:
        flash('Not enough coins to redeem. You need at least 500 coins.', 'danger')

    conn.close()  # Close the database connection
    return redirect(url_for('transaction'))  # Redirect back to the transaction page



# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('signin'))



@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Save the user data in a text file (not recommended for production)
        with open('contact.txt', 'a') as file:
            file.write(f"Username: {username}, Email: {email}, Subject: {subject}, Message: {message}\n")
        return redirect(url_for('contact'))
    return render_template('contact.html')  # Make sure to have a contact.html template for rendering

            



            
if __name__ == '__main__':
    app.run(debug=True)
