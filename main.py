from flask import Flask, render_template, request, redirect, url_for, make_response
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            user='u321595372_shishukunj123',
            password='Balvigyan@2024',
            host='www.atts.site',
            database='u321595372_tolltaxsystem',
            port=3306,
            connection_timeout=5
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
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error: {e}")

    # Create response without caching for dynamic data
    response = make_response(render_template('home.html', plazas=plazas))
    # Set no-cache for dynamic data
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        response = make_response(render_template('pages/add.html'))
        response.headers['Cache-Control'] = 'no-store'  # Don't cache forms
        return response

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
    return redirect(url_for('home'))


@app.route('/edit/<int:plaza_code>', methods=['GET', 'POST'])
def edit(plaza_code):
    if request.method == 'GET':
        conn = get_db_connection()
        if conn is not None:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT * FROM toll_tbl WHERE t_code = %s', (plaza_code,))
                plaza = cursor.fetchone()
                cursor.close()
                conn.close()
                if plaza:
                    response = make_response(render_template('pages/edit.html', plaza=plaza))
                    response.headers['Cache-Control'] = 'no-store'  # Don't cache forms
                    return response
                return "Plaza not found", 404
            except Error as e:
                print(f"Error: {e}")
                return f"An error occurred: {str(e)}"

    if request.method == 'POST':
        conn = get_db_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
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
                cursor.close()
                conn.close()
                return redirect(url_for('home'))
            except Error as e:
                print(f"Error: {e}")
                return f"An error occurred: {str(e)}"
    return redirect(url_for('home'))


@app.route('/delete/<plaza_code>')
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


if __name__ == '__main__':
    app.run(debug=True)