from flask import Flask, render_template, request, flash, redirect, url_for
import psycopg2
import hashlib

app = Flask(__name__)


# Функция создания подключения к бд
def get_db_connection():
    connector = psycopg2.connect(host='localhost',
                                 database='flask_db',
                                 user="postgres",
                                 password="postgres")
    return connector


conn = get_db_connection()
cur = conn.cursor()

# Пример создания таблицы с данными
cur.execute('DROP TABLE IF EXISTS books;')
cur.execute('CREATE TABLE books (id serial PRIMARY KEY,'
            'title varchar (150) NOT NULL,'
            'author varchar (50) NOT NULL,'
            'pages_num integer NOT NULL,'
            'review text,'
            'date_added date DEFAULT CURRENT_TIMESTAMP);'
            )

cur.execute('INSERT INTO books (title, author, pages_num, review)'
            'VALUES (%s, %s, %s, %s)',
            ('A Tale of Two Cities',
             'Charles Dickens',
             489,
             'A great classic!')
            )

cur.execute('INSERT INTO books (title, author, pages_num, review)'
            'VALUES (%s, %s, %s, %s)',
            ('Anna Karenina',
             'Leo Tolstoy',
             864,
             'Another great classic!')
            )

conn.commit()

cur.close()
conn.close()


# Дальше функии приложения
@app.route('/')
@app.route("/index")
def index():
    conn1 = get_db_connection()
    cur1 = conn1.cursor()
    cur1.execute('SELECT * FROM books;')
    books = cur1.fetchall()
    cur1.close()
    conn1.close()
    flash('Ваш email будет использован только для регистрации!')
    return render_template('index.html', books=books)


@app.route('/auth', methods=('GET', 'POST'))
def auth():
    if request.method == 'POST':
        login = request.form['email']
        passwd = request.form['password']
        pg_passwd = login + passwd
        md5_hash = hashlib.md5()
        encoded = bytes(pg_passwd, encoding='utf-8')
        md5_hash.update(encoded)
        full_hash = 'md5' + md5_hash.hexdigest()
        conn1 = get_db_connection()
        cur1 = conn1.cursor()
        cur1.execute("SELECT EXISTS (SELECT * FROM pg_shadow WHERE usename = '" + login + "' AND passwd = '" + full_hash + "');")
        result = cur1.fetchone()
        cur1.close()
        conn1.close()
        flash(result)
        if result[0] == True:
            return redirect(url_for("site"))
        return redirect(url_for("index"))
    return render_template('index.html')


@app.route("/site")
def site():
    return render_template('site.html')


if __name__ == "__main__":
    app.secret_key = 'admin123'
    app.run(debug=False)
