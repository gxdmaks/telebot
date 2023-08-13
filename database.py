import sqlite3
from datetime import datetime

# создаем подключение
connection = sqlite3.connect('dostavka.db')
# пеходчик/исполнитель
sql = connection.cursor()

# создаем запрос на создание таблицы (пользователи,склад,корзина)
sql.execute('CREATE TABLE IF NOT EXISTS users(tg_id INTEGER, name TEXT, phone_number TEXT, address TEXT,reg_date DATETIME);')
# создаем таблицу для склада
sql.execute('CREATE TABLE IF NOT EXISTS products(pr_id INTEGER PRIMARY KEY AUTOINCREMENT , pr_name TEXT, pr_price REAL, pr_quantity INTEGER, pr_des DATETIME, pr_photo TEXT, pr_reg_date DATETIME);')
# создаем таблицу для корзины
sql.execute('CREATE TABLE IF NOT EXISTS korzina(tg_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, user_room, quantity INTEGER, total_for_room REAL);')

def register_user(tg_id, name, phone_number, address):
    connection = sqlite3.connect('dostavka.db')
    # пеходчик/исполнитель
    sql = connection.cursor()
    sql.execute('INSERT INTO users '
                '(tg_id, name, phone_number, address,reg_date) VALUES'
                '(?, ?, ?, ?, ?);', (tg_id, name, phone_number, address, datetime.now()))

    # записать обновления
    connection.commit()

# проверка пользователя есь ли он в базе
def check_user(user_id):
    connection = sqlite3.connect('dostavka.db')
    # переходчик/исполнитель
    sql = connection.cursor()
    checker = sql.execute('SELECT tg_id FROM users WHERE tg_id=?;', (user_id, ))
    if checker.fetchone():
        return True

    else:
        return False

#(ДЗ) добавление в склад(products)
def dob(pr_name,pr_price,pr_quantity,pr_des,pr_photo):
    connection = sqlite3.connect('dostavka.db')
    # пеходчик/исполнитель
    sql = connection.cursor()
    sql.execute('INSERT INTO products '
                '(pr_name, pr_price, pr_quantity, pr_des, pr_photo) VALUES '
                '(?, ?, ?, ?, ?);', (pr_name, pr_price, pr_quantity,pr_des,pr_photo))

    connection.commit()

def delete_from_sklad():
    connection = sqlite3.connect('dostavka.db')
    sql = connection.cursor()
    sql.execute('DELETE FROM product;')

def delete_execute_from_products(pr_id):
    connection = sqlite3.connect('dostavka.db')
    sql = connection.cursor()
    sql.execute('DELETE FROM products WHERE pr_id=?;',(pr_id, ))

# получить все продукты из базы (name, id)
def get_pr_name_id():
    connection = sqlite3.connect('dostavka.db')
    sql=connection.cursor()
    # получаем все продукты из базы
    products = sql.execute('SELECT pr_name, pr_id, pr_quantity FROM products').fetchall()
    # сортеруем только те что остались на складе
    sorted_product = [(i[0], i[1]) for i in products if i[2] > 0]
    # чистый список продуктов
    return  sorted_product


def get_pr_id():
    connection = sqlite3.connect('dostavka.db')
    sql=connection.cursor()
    # получаем все продукты из базы
    products = sql.execute('SELECT pr_name, pr_id, pr_quantity FROM products').fetchall()
    # сортеруем только те что остались на складе
    sorted_product = [i[1] for i in products if i[2] > 0]
    # чистый список продуктов
    return  sorted_product
# получение инфы про определенный продукт (через pr_id) -> (photo,des,price)
def get_exact_product(pr_id):
    connection = sqlite3.connect('dostavka.db')
    sql=connection.cursor()
    exact_product = sql.execute('SELECT pr_photo, pr_des, pr_price FROM products WHERE pr_id=?;', (pr_id, )).fetchone()

    return  exact_product

# добфвление проодуктов в корзину пользователя
def add_product(user_id, product, quantity):
    connection = sqlite3.connect('dostavka.db')
    sql = connection.cursor()

    product_price = get_exact_product(product)[2]

    sql.execute('INSERT INTO korzina '
                      '(user_id,user_product,quantity, total_for_product)'
                      'VALUES (?, ?, ?, ?);',(user_id,product,quantity,quantity * product_price))

    connection.commit()

    # удаление
def delete_exect_kor(pr_id, user_id):
    connection = sqlite3.connect('dostavka.db')
    sql = connection.cursor()
    sql.execute('DELETE FROM korzina WHERE user_product = ? AND user_id=?;', (pr_id,user_id))
    # сохраняем изменения
    connection.commit()

# Вывод корзины пользователя через (user_id) -> [(product, quantity, total_for_product),(product, quantity, total_for_product),(product, quantity, total_for_product)]
def get_exect_korzina(user_id):
    connection = sqlite3.connect('dostavka.db')
    sql = connection.cursor()

    korzina = sql.execute('SELECT products.pr_name,korzina.quantity,'
                          ' korzina.total_for_product FROM korzina '
                          ' INNER JOIN products ON pr_id=korzina.user_product'
                          ' WHERE user_id = ?;',(user_id, )).fetchall()
    return korzina
def delete_kor(user_id):
    connection = sqlite3.connect('dostavka.db')
    sql = connection.cursor()
    sql.execute('DELETE FROM korzina WHERE user_id=?;', (user_id,))
    # сохраняем изменения
    connection.commit()
# удаление продуктов из склада(ДЗ)

# Получить номер телефона и имя пользователя
def get_user_number_name(user_id):
    connection = sqlite3.connect('dostavka.db')
    sql = connection.cursor()
    exect_user = sql.execute('SELECT name, phone_number FROM users WHERE tg_id=?;', (user_id, ))
    return exect_user.fetchone()