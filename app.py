import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret'

DATABASE = 'hotel.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (username, password, email) VALUES (?, ?, ?)", (username, hashed_password, email))
        conn.commit()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        user = cursor.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect(url_for('rooms'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/rooms')
def rooms():
    conn = get_db()
    cursor = conn.cursor()
    rooms = cursor.execute("SELECT * FROM room").fetchall()
    return render_template('rooms.html', rooms=rooms)

@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
def book(room_id):
    conn = get_db()
    cursor = conn.cursor()
    room = cursor.execute("SELECT * FROM room WHERE id = ?", (room_id,)).fetchone()

    if request.method == 'POST':
        user_id = session.get('user_id')
        full_name = request.form.get('full_name')
        NIK = request.form.get('NIK')
        check_in_date = request.form.get('check_in_date')
        check_out_date = request.form.get('check_out_date')
        payment_method = request.form.get('payment_method')

        cursor.execute("INSERT INTO booking (user_id, room_id, full_name, NIK, check_in_date, check_out_date, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, room_id, full_name, NIK, check_in_date, check_out_date, payment_method))
        cursor.execute("UPDATE room SET availability = 0 WHERE id = ?", (room_id,))
        conn.commit()

        flash('Booking successful!', 'success')
        return redirect(url_for('index'))
    return render_template('book.html', room=room)

if __name__ == '__main__':
    app.run(debug=True)