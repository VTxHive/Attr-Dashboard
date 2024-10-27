from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from functools import wraps
import time

app = Flask(__name__)

# Connection Pool Configuration
dbconfig = {
    "pool_name": "mypool",
    "pool_size": 5,
    "user": 'u321595372_shishukunj123',
    "password": 'Balvigyan@2024',
    "host": 'www.atts.site',
    "database": 'u321595372_tolltaxsystem',
    "port": 3306
}

# Initialize the connection pool
try:
    connection_pool = MySQLConnectionPool(**dbconfig)
except Error as e:
    print(f"Error connecting to MySQL: {e}")
    connection_pool = None

def get_db_connection():
    if connection_pool:
        return connection_pool.get_connection()
    return None

# Database connection context manager
class DatabaseConnection:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = get_db_connection()
        if self.conn:
            self.cursor = self.conn.cursor(dictionary=True)
            return self.cursor
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# Cache decorator
def cache_with_timeout(timeout=300):  # 5 minutes default
    def decorator(f):
        cache = {}
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = str(args) + str(kwargs)
            now = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < timeout:
                    return result
            result = f(*args, **kwargs)
            cache[key] = (result, now)
            return result
        return decorated_function
    return decorator

@app.route('/')
@cache_with_timeout(timeout=60)  # Cache for 1 minute
def home():
    with DatabaseConnection() as cursor:
        if cursor:
            try:
                cursor.execute('SELECT * FROM toll_tbl')
                plazas = cursor.fetchall()
                return render_template('home.html', plazas=plazas)
            except Error as e:
                print(f"Error: {e}")
                return "Database error", 500
        return "Could not connect to database", 500

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        with DatabaseConnection() as cursor:
            if cursor:
                try:
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
                    cursor.connection.commit()
                    return redirect(url_for('home'))
                except Error as e:
                    print(f"Error: {e}")
                    return f"An error occurred: {str(e)}"
    return render_template('pages/add.html')

@app.route('/edit/<int:plaza_code>', methods=['GET', 'POST'])
def edit(plaza_code):
    with DatabaseConnection() as cursor:
        if cursor:
            try:
                if request.method == 'GET':
                    cursor.execute('SELECT * FROM toll_tbl WHERE t_code = %s', (plaza_code,))
                    plaza = cursor.fetchone()
                    if plaza:
                        return render_template('pages/edit.html', plaza=plaza)
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
                    cursor.connection.commit()
                    return redirect(url_for('home'))
            except Error as e:
                print(f"Error: {e}")
                return f"An error occurred: {str(e)}"
    return redirect(url_for('home'))

@app.route('/delete/<plaza_code>')
def delete(plaza_code):
    with DatabaseConnection() as cursor:
        if cursor:
            try:
                cursor.execute('DELETE FROM toll_tbl WHERE t_code = %s', (plaza_code,))
                cursor.connection.commit()
                return redirect(url_for('home'))
            except Error as e:
                print(f"Error: {e}")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)