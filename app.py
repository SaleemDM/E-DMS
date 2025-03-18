import os
from flask import Flask, request, redirect, url_for, render_template, flash
import mysql.connector
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# MySQL Configuration
DB_CONFIG = {
    'host': 'host.docker.internal',
    'user': 'root',
    'password': 'root',
    'database': 'edms_db'
}

# Flask Extensions
app.secret_key = 'your_secret_key'  # Required for session management
bcrypt = Bcrypt(app)               # For password hashing
login_manager = LoginManager(app)   # Manages user sessions
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    connection.close()

    if user_data:
        return User(*user_data)
    return None

# Home page
@app.route('/')
def home():
    return '''
    <h1>EDMS - Upload System</h1>
    <p><a href="/register">Register</a> | <a href="/login">Login</a></p>
    '''

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('login'))

    return '''
    <h2>Register</h2>
    <form method="POST">
        Username: <input type="text" name="username" required><br>
        Password: <input type="password" name="password" required><br>
        <input type="submit" value="Register">
    </form>
    '''

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()

        if user_data and bcrypt.check_password_hash(user_data[2], password):
            user = User(*user_data)
            login_user(user)
            return redirect(url_for('upload_file'))

        return "Invalid username or password"

    return '''
    <h2>Login</h2>
    <form method="POST">
        Username: <input type="text" name="username" required><br>
        Password: <input type="password" name="password" required><br>
        <input type="submit" value="Login">
    </form>
    '''

# User Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Upload Document (Only for Authenticated Users)
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file provided!", 400

        file = request.files['file']

        if file.filename == '':
            return "No selected file", 400

        # Save file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Save metadata to MySQL
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            upload_time = datetime.now()
            cursor.execute("INSERT INTO documents (filename, upload_time) VALUES (%s, %s)", (file.filename, upload_time))
            connection.commit()
            cursor.close()
            connection.close()
            return f"File uploaded successfully: {file.filename}"
        except Exception as e:
            return f"Error saving to database: {e}", 500

    return '''
    <h2>Upload Document</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload File">
    </form>
    <p><a href="/logout">Logout</a></p>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
