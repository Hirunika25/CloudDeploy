"""
app.py
------
A very simple Login System using Flask + MySQL.

Features:
1. Register (Sign Up) a new user
2. Login an existing user
3. Dashboard (only visible after login)
4. Logout

Beginner notes are written as comments (#) throughout the code.
"""

# ---------- 1. IMPORT THE TOOLS WE NEED ----------
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

# Load variables from the .env file (DB password, secret key, etc.)
load_dotenv()

# ---------- 2. CREATE THE FLASK APP ----------
app = Flask(__name__)

# Secret key is needed so Flask can safely remember "sessions" (who is logged in)
app.secret_key = os.getenv("SECRET_KEY")

# ---------- 3. MYSQL CONFIGURATION ----------
# These values are read from the .env file
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # lets us access columns by name

mysql = MySQL(app)

# ---------- 4. HOME PAGE ----------
@app.route('/')
def home():
    return render_template('home.html')


# ---------- 5. REGISTER (SIGN UP) PAGE ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get data submitted from the form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Hash (scramble) the password before saving it.
        # We NEVER store plain text passwords in the database.
        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        # Check if email already exists
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Email already registered. Please login.", "danger")
            cur.close()
            return redirect(url_for('register'))

        # Insert the new user into the database
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        mysql.connection.commit()
        cur.close()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    # If it's just a GET request, show the register form
    return render_template('register.html')


# ---------- 6. LOGIN PAGE ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        # Check if user exists AND password matches the hashed password
        if user and check_password_hash(user['password'], password):
            # Save info in the session so we know this user is logged in
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


# ---------- 7. DASHBOARD (PROTECTED PAGE) ----------
@app.route('/dashboard')
def dashboard():
    # Only allow access if the user is logged in
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    return render_template('dashboard.html', name=session['user_name'])


# ---------- 8. LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()  # remove all session data (log the user out)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# ---------- 9. RUN THE APP ----------
if __name__ == '__main__':
    # debug=True is helpful while developing (shows errors in browser)
    # Turn debug=False when you deploy to the cloud for production
    app.run(debug=True, host='0.0.0.0', port=5000)
