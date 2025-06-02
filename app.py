from flask import Flask, render_template, request, redirect, session, send_from_directory, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os, sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'


# Initialize database
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')


@app.route('/')
def index():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:
            with sqlite3.connect('database.db') as conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], username), exist_ok=True)
            return redirect('/login')
        except:
            return "User already exists!"
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[0], password):
                session['user'] = username
                return redirect('/upload')
            else:
                return "Invalid credentials!"
    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user' not in session:
        return redirect('/login')

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['user'])

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(user_folder, filename))
            return redirect('/files')

    return render_template('upload.html')


@app.route('/files')
def list_files():
    if 'user' not in session:
        return redirect('/login')

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['user'])
    files = os.listdir(user_folder)
    return render_template('files.html', files=files)


@app.route('/download/<filename>')
def download_file(filename):
    if 'user' not in session:
        return redirect('/login')

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['user'])
    return send_from_directory(user_folder, filename, as_attachment=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
