from flask import Flask, render_template, request, flash, redirect, url_for
import psycopg2
import hashlib
import json
from flask_login import LoginManager, login_required, login_user
from login import UserLogin

app = Flask(__name__)
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
            'date_added date DEFAULT CURRENT_TIMESTAMP);'
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

cur.execute('INSERT INTO books (title, author, pages_num, cost, review)'
            'VALUES (%s, %s, %s, %s, %s)',
            ('Этичный хакинг. Практическое руководство',
             'Дэниел Г. Грэм',
             384,
             235,
             'Практическое руководство по взлому компьютерных систем с нуля, от перехвата трафика до создания троянов.')
            )

cur.execute('INSERT INTO books (title, author, pages_num, cost, review)'
            'VALUES (%s, %s, %s, %s, %s)',
            ('Безопасность веб-приложений.',
             'Эндрю Хоффман',
             336,
             550,
             'Познакомьтесь на практике с разведкой, защитой и нападением! Методы эффективного анализа веб-приложений.')
            )

cur.execute('INSERT INTO books (title, author, pages_num, cost, review)'
            'VALUES (%s, %s, %s, %s, %s)',
            ('Грокаем алгоритмы. Иллюстрированное пособие',
             'Адитья Бхаргава',
             288,
             300,
             'Алгоритмы – это всего лишь пошаговое решения задач, а грокать алгоритмы – это весело и увлекательно.'))


cur.execute('INSERT INTO books (title, author, pages_num, cost, review)'
            'VALUES (%s, %s, %s, %s, %s)',
            ('Компьютерные сети. Принципы, технологии, протоколы',
             'Виктор Олифер, Наталья Олифер',
             1005,
             699,
             'Издание предназначено для студентов, аспирантов и технических специалистов.')
            )

cur.execute('INSERT INTO books (title, author, pages_num, cost, review)'
            'VALUES (%s, %s, %s, %s, %s)',
            ('Astra Linux. Руководство',
             'Елена Вовк',
             580,
             899,
             'Практическое руководство по использованию российской операционной системы Astra Linux.')
            )

cur.execute('INSERT INTO books (title, author, pages_num, cost, review)'
            'VALUES (%s, %s, %s, %s, %s)',
            ('Думай медленно… Решай быстро',
             'Даниэль Канеман',
             710,
             990,
             'Наши действия и поступки определены нашими мыслями. Но всегда ли мы контролируем наше мышление?')
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


@app.route('/test')
def test():
    conn1 = get_db_connection()
    cur1 = conn1.cursor()
    cur1.execute("SELECT * FROM pg_shadow WHERE usename = 'postgres';")
    result = cur1.fetchone()
    cur1.close()
    conn1.close()
    print(result[1])
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
        cur1.execute("SELECT * FROM pg_shadow WHERE usename = '" + login + "';")
        user = cur1.fetchone()
        cur1.close()
        conn1.close()
        flash(result)
        if result[0] == True:
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for("shop"))
        return redirect(url_for("index"))
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
    result = cur1.fetchone()
    cur1.close()
    conn1.close()
    if result[2] == 100:
        return json.dumps({'coupon': result, 'payment': 'True'})
    return json.dumps({'coupon': result, 'payment': 'False'})


if __name__ == "__main__":
    app.secret_key = 'admin123'
    app.run(debug=False)
