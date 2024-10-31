# main.py
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.permanent_session_lifetime = timedelta(hours=1)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            user='u321595372_shishukunj123',
            password='Balvigyan@2024',
            host='www.atts.site',
            database='u321595372_tolltaxsystem',
            port=3306
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


@app.route('/')
def home():
    conn = get_db_connection()
    plazas = []
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM toll_tbl')
            plazas = cursor.fetchall()
            print(plazas)
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error: {e}")
    return render_template('home.html', plazas=plazas)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO toll_tbl
                    (t_code, t_name, concessionaire_type, t_type, 
                     t_sub_type, t_state, t_city, concessionaire_name, geo_code)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    request.form['plaza_code'],
                    request.form['name'],
                    request.form['concessionaire_type'],
                    request.form['plaza_type'],
                    request.form['plaza_sub_type'],
                    request.form['state'],
                    request.form['city'],
                    request.form['concessionaire'],
                    request.form['geo_codes']
                ))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('home'))
            except Error as e:
                print(f"Error: {e}")
                return f"An error occurred: {str(e)}"
    return render_template('pages/add.html')


# main.py (relevant section with fixes)

@app.route('/edit/<int:plaza_code>', methods=['GET', 'POST'])
@login_required
def edit(plaza_code):
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary=True)
            if request.method == 'GET':
                # Fetch the existing toll plaza data
                cursor.execute('SELECT * FROM toll_tbl WHERE t_code = %s', (plaza_code,))
                plaza = cursor.fetchone()
                print(plaza)
                if plaza:
                    return render_template('pages/edit.html', plaza=plaza)
                else:
                    return "Plaza not found", 404

            elif request.method == 'POST':
                cursor.execute('''
                    UPDATE toll_tbl 
                    SET t_name=%s, concessionaire_type=%s, t_type=%s,
                        t_sub_type=%s, t_state=%s, t_city=%s,
                        concessionaire_name=%s, geo_code=%s
                    WHERE t_code=%s
                ''', (
                    request.form['name'],
                    request.form['concessionaire_type'],
                    request.form['plaza_type'],
                    request.form['plaza_sub_type'],
                    request.form['state'],
                    request.form['city'],
                    request.form['concessionaire'],
                    request.form['geo_codes'],
                    plaza_code
                ))
                conn.commit()
                return redirect(url_for('home'))
        except Error as e:
            print(f"Error: {e}")
            return f"An error occurred: {str(e)}"
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('home'))


@app.route('/delete/<plaza_code>')
@login_required
def delete(plaza_code):
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM toll_tbl WHERE t_code = %s', (plaza_code,))
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error: {e}")
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user:
                    if user[2] == password:
                        session.permanent = True
                        session['user'] = user
                        return redirect(url_for('home'))
                    else:
                        return render_template('pages/login.html', error='Invalid username or password')
                else:
                    return render_template('pages/login.html', error='User Not Found')

            except Error as e:
                print(f"Error: {e}")
                return f"An error occurred: {str(e)}"
            finally:
                cursor.close()
                conn.close()

    return render_template('pages/login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()  # Clears all session data
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
