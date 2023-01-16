from flask import Flask, render_template, Response, request, render_template_string
import psycopg2

app = Flask(__name__)


# Функция создания подключения к бд
def get_db_connection():
    connector = psycopg2.connect(host='localhost',
                            database='flask_db',
                            user="admin",
                            password="admin")
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
def index():
    conn1 = get_db_connection()
    cur1 = conn1.cursor()
    cur1.execute('SELECT * FROM books;')
    books = cur1.fetchall()
    cur1.close()
    conn1.close()
    return render_template('index.html', books=books)


if __name__ == "__main__":
    app.run(debug=False)
