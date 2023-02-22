from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
import psycopg2
import hashlib
import json
from flask_login import LoginManager, login_required, login_user
from login import UserLogin
from os import path

DOWNLOAD_FOLDER = '/books'

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
login_manager = LoginManager(app)


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
            'cost integer NOT NULL,'
            'review text,'
            'date_added date DEFAULT CURRENT_TIMESTAMP,'
            'key varchar (10),'
            'filename varchar (150) NOT NULL);'
            )

cur.execute('DROP TABLE IF EXISTS coupons;')
cur.execute('CREATE TABLE coupons (id serial PRIMARY KEY,'
            'coupon varchar (150) NOT NULL,'
            'discount integer NOT NULL);'
            )

cur.execute('INSERT INTO coupons (coupon, discount)'
            'VALUES (%s, %s)',
            ('kaf33', 15)
            )

cur.execute('INSERT INTO coupons (coupon, discount)'
            'VALUES (%s, %s)',
            ('maxim', 20)
            )

cur.execute('INSERT INTO coupons (coupon, discount)'
            'VALUES (%s, %s)',
            ('fake', 100)
            )

cur.execute('INSERT INTO books (title, author, pages_num, cost, review, key, filename)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            ('Этичный хакинг. Практическое руководство',
             'Дэниел Г. Грэм',
             384,
             235,
             'Практическое руководство по взлому компьютерных систем с нуля, от перехвата трафика до создания троянов.',
             'qwerty123',
             'Deniel_G._Grem_Etichnyiy_haking.pdf')
            )

cur.execute('INSERT INTO books (title, author, pages_num, cost, review, key, filename)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            ('Безопасность веб-приложений.',
             'Эндрю Хоффман',
             336,
             550,
             'Познакомьтесь на практике с разведкой, защитой и нападением! Методы эффективного анализа веб-приложений.',
             'qwerty123',
             'Deniel_G._Grem_Etichnyiy_haking.pdf')
            )

cur.execute('INSERT INTO books (title, author, pages_num, cost, review, key, filename)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            ('Грокаем алгоритмы. Иллюстрированное пособие',
             'Адитья Бхаргава',
             288,
             300,
             'Алгоритмы – это всего лишь пошаговое решения задач, а грокать алгоритмы – это весело и увлекательно.',
             'qwerty123',
             'Deniel_G._Grem_Etichnyiy_haking.pdf')
            )


cur.execute('INSERT INTO books (title, author, pages_num, cost, review, key, filename)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            ('Компьютерные сети. Принципы, технологии, протоколы',
             'Виктор Олифер, Наталья Олифер',
             1005,
             699,
             'Издание предназначено для студентов, аспирантов и технических специалистов.',
             'qwerty123',
             'Deniel_G._Grem_Etichnyiy_haking.pdf')
            )

cur.execute('INSERT INTO books (title, author, pages_num, cost, review, key, filename)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            ('Astra Linux. Руководство',
             'Елена Вовк',
             580,
             899,
             'Практическое руководство по использованию российской операционной системы Astra Linux.',
             'qwerty123',
             'Deniel_G._Grem_Etichnyiy_haking.pdf')
            )

cur.execute('INSERT INTO books (title, author, pages_num, cost, review, key, filename)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            ('Думай медленно… Решай быстро',
             'Даниэль Канеман',
             710,
             990,
             'Наши действия и поступки определены нашими мыслями. Но всегда ли мы контролируем наше мышление?',
             'qwerty123',
             'Deniel_G._Grem_Etichnyiy_haking.pdf')
            )

conn.commit()

cur.close()
conn.close()


@login_manager.user_loader
def load_user(login):
    print("load_user")
    conn1 = get_db_connection()
    cur1 = conn1.cursor()
    loader = UserLogin().fromDB(login, cur1)
    cur1.close()
    conn1.close()
    return loader


# Дальше функии приложения
@app.route('/')
@app.route("/index")
def index():
    flash('Ваш email будет использован только для регистрации!')
    return render_template('index.html')


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
        flash(result)
        print(result)
        if result[0] == True:
            cur1.execute("SELECT * FROM pg_shadow WHERE usename = '" + login + "';")
            user = cur1.fetchone()
            cur1.close()
            conn1.close()
            user_login = UserLogin().create(user)
            login_user(user_login)
            return redirect(url_for("shop"))
        else:
            cur1.close()
            conn1.close()
            return redirect(url_for("index"))
        cur1.close()
        conn1.close()
    return render_template('index.html')


@app.route('/shop', methods=('GET', 'POST'))
@login_required
def shop():
    conn1 = get_db_connection()
    cur1 = conn1.cursor()
    cur1.execute('SELECT * FROM books;')
    books = cur1.fetchall()
    cur1.close()
    conn1.close()
    return render_template('shop.html', books=books)


@app.route("/buy/<int:book_id>", methods=['GET', 'POST'])
@login_required
def buy(book_id):
    conn1 = get_db_connection()
    cur1 = conn1.cursor()
    book_id1 = book_id
    cur1.execute("SELECT * FROM books WHERE id = " + str(book_id1) + ";")
    book = cur1.fetchone()
    cur1.close()
    conn1.close()
    return render_template('buy.html', book=book)


@app.route('/pay', methods=('GET', 'POST'))
@login_required
def pay():
    discount = request.form['coupon']
    conn1 = get_db_connection()
    cur1 = conn1.cursor()
    cur1.execute("SELECT * FROM coupons WHERE coupon = '" + discount + "';")
    result = cur1.fetchall()
    cur1.close()
    conn1.close()
    print(result)
    try:
        if result[2] == 100:
            return json.dumps({'coupon': result, 'payment': 'True'})
    except TypeError:
        json.dumps({'coupon': result, 'payment': 'False'})
    except IndexError:
        json.dumps({'coupon': result, 'payment': 'False'})
    return json.dumps({'coupon': result, 'payment': 'False'})


@app.route('/get_key', methods=('GET', 'POST'))
@login_required
def get_key():
    book_id = request.form['book_id']
    print(book_id)
    conn1 = get_db_connection()
    cur1 = conn1.cursor()
    cur1.execute("SELECT key FROM books WHERE id = '" + book_id + "';")
    download_key = cur1.fetchone()
    cur1.close()
    conn1.close()
    return json.dumps({'key': download_key[0]})


@app.route('/download', methods=('GET', 'POST'))
@login_required
def download():
    download_key = request.form['download_key']
    book_id = request.form['book_id']
    print(download_key)
    print(book_id)
    conn1 = get_db_connection()
    cur1 = conn1.cursor()
    cur1.execute("SELECT key FROM books WHERE id = '" + book_id + "';")
    db_key = cur1.fetchone()
    if download_key == db_key[0]:
        cur1.execute("SELECT filename FROM books WHERE id = '" + book_id + "';")
        filename = cur1.fetchone()
        cur1.close()
        conn1.close()
        path = 'downloads'
        return send_from_directory(path, filename[0], as_attachment=True)
    cur1.close()
    conn1.close()
    return json.dumps({'Oops': 'Oops!'})


if __name__ == "__main__":
    app.secret_key = 'admin123'
    app.run(debug=False)
