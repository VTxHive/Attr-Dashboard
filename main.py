# main.py
from flask import Flask, render_template, request, redirect, url_for
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
            port=3306
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def init_db():
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor(buffered=True)

            # Create toll_plazas table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS toll_plazas
                            (plaza_code VARCHAR(50) PRIMARY KEY,
                             name VARCHAR(255) NOT NULL,
                             concessionaire_type VARCHAR(100),
                             plaza_type VARCHAR(100),
                             plaza_sub_type VARCHAR(100),
                             state VARCHAR(100),
                             city VARCHAR(100),
                             concessionaire VARCHAR(255),
                             geo_codes VARCHAR(100))''')

            conn.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()


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
    init_db()
    app.run(debug=True)