from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file, render_template_string
import sqlite3
import subprocess
from werkzeug.security import generate_password_hash, check_password_hash
import os

from config import UPLOAD_FOLDER, secret_key
from databases_functions import get_db_connection_users, get_db_connection_books, get_db_connection_reviews

app = Flask(__name__)

app.secret_key = secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection_users()
        query = f"SELECT * FROM users WHERE name = '{username}' and password = '{password}'"
        user = conn.execute(query).fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Пароли не совпадают!')
            return redirect(url_for('register'))

        conn = get_db_connection_users()
        existing_user = conn.execute('SELECT * FROM users WHERE name = ?', (username,)).fetchone()

        if existing_user:
            flash('Такой пользователь уже существует!', 'error')
            conn.close()
            return redirect(url_for('register'))
        try:
            conn.execute('INSERT INTO users (name, password) VALUES (?, ?)', (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('An error occurred, please try again.', 'error')
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('register_page.html')


@app.route('/home')
def home():
    if 'username' in session:
        conn = get_db_connection_books()
        books = conn.execute('SELECT * FROM books').fetchall()
        conn.close()
        return render_template('home.html', books=books)
    return redirect(url_for('login'))


@app.route('/view_cover')
def view_cover():
    cover_path = request.args.get('cover_path')
    if cover_path:
        try:
            return send_file(cover_path)
        except Exception as e:
            return str(e)
    return 'Путь к обложке не указан'


@app.route('/reviews')
def view_reviews():
    conn = get_db_connection_reviews()
    reviews = conn.execute('SELECT * FROM reviews').fetchall()
    conn.close()
    return render_template_string(open('templates/review_page.html').read(), reviews=reviews)


@app.route('/post_review', methods=['GET', 'POST'])
def post_review():
    conn = get_db_connection_reviews()
    if request.method == 'POST':
        book_title = request.form['book_title']
        review_text = request.form['review']
        conn.execute('INSERT INTO reviews (title, review) VALUES (?, ?)', 
                     (book_title, review_text))
        conn.commit()
        conn.close()
        return redirect(url_for('view_reviews'))

    return render_template_string(open('templates/review_page.html').read())


@app.route('/upload', methods=['GET', 'POST'])
def upload_book():
    if request.method == 'POST':
        book_title = request.form['title']
        author = request.form['author']
        file = request.files['file']
        filename = file.filename
        if file:
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filepath = os.path.join('uploads/', filename)
                out = subprocess.check_output((f"convert -resize 99% {UPLOAD_FOLDER}{filename} {UPLOAD_FOLDER}backup.jpg"), shell=True)
                conn = get_db_connection_books()
                conn.execute('INSERT INTO books (title, author, cover_path) VALUES (?, ?, ?)', 
                (book_title, author, filepath))
                conn.commit()
                conn.close()
            except Exception as e:
                return 'Error: ' + str(e) 
        return redirect(url_for('home'))
    return render_template('upload_book.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
