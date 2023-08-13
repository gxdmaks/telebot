import database
import button
import telebot
from telebot.types import ReplyKeyboardRemove
from geopy.geocoders import Nominatim
# создаем

bot = telebot.TeleBot('6110677582:AAFlxD4_OunzLZ9ccCiothU0jj1jc3vcZ7A')
geolocator = Nominatim(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/113.0.0.0 Safari/537.36')
# Словарь для временных данных
users = {}

# database.dob('Яблоко',12000,12,'Самый лучший дорогой','https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.healthline.com%2Fnutrition%2F10-health-benefits-of-apples&psig=AOvVaw3OKC6bDzeIkR01N-agCafE&ust=1685200026974000&source=images&cd=vfe&ved=0CBEQjRxqFwoTCPj0ksqhk_8CFQAAAAAdAAAAABAE')
# database.dob('Груша',30000,1,'Биг грин пэнсил','https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.nofrills.ca%2Fenglish-cucumber%2Fp%2F20070132001_EA&psig=AOvVaw1K0ooW5IuOwv2u_E-5a7Bw&ust=1685201984715000&source=images&cd=vfe&ved=0CBEQjRxqFwoTCNC5hPCok_8CFQAAAAAdAAAAABAE')
# обработка команды старт


@bot.message_handler(commands=['start'])

def start(message):
    # полувчить теграмм айди
    user_id = message.from_user.id
    print(user_id)
    # проверка пользователя
    checker = database.check_user(user_id)
    #  если юзер есть в базе
    if checker:
        # получим актульный список продуктов
        products = database.get_pr_name_id()
        # отправим сообщение с меню\
        bot.send_message(user_id,'Привет',reply_markup=ReplyKeyboardRemove())
        bot.send_message(user_id, ' выберите пункт меню', reply_markup=button.main_menu_kb(products))
    elif not checker:
        bot.send_message(user_id, ' привет\nотправь имя')
        bot.register_next_step_handler(message, get_name)
        #  переход на этап получения имени(дз)


@bot.message_handler(content_types=['text'])
def get_name(message):
    user_id = message.from_user.id
    name = message.text
    bot.send_message(user_id, 'отправь свой номер', reply_markup=button.phone_number_kb())
    bot.register_next_step_handler(message, get_number, name)


def get_number(message, name):
    user_id = message.from_user.id
    if message.contact:
        # созраним контакт
        phone_number = message.contact.phone_number
        # сохраняем его в базе
        database.register_user(user_id, name, phone_number, 'Not yet')
        # торываем меню
        products = database.get_pr_name_id()
        bot.send_message(user_id,'Привет',reply_markup=ReplyKeyboardRemove())
        bot.send_message(user_id, 'выберите пункт меню', reply_markup=button.main_menu_kb(products))
    elif not message.contact:
        bot.send_message(user_id, 'отправьте свой номер используя кнопку!', reply_markup=button.phone_number_kb())
        bot.register_next_step_handler(message, get_number, name)
    # вызов data_base.register_user(user_id, name , phone_number, "not yet")
    # bot.send_message(user_id, 'menu',reply_markup=butt.main_menu(products)
@bot.callback_query_handler(lambda call: call.data in ['increment','decrement','add_to_cart','back'])
def get_user_product_count(call):
    user_id = call.message.chat.id
    if call.data == 'increment':
        actual_count = users[user_id]['pr_count']
        users[user_id]['pr_count'] += 1
        bot.edit_message_reply_markup(chat_id=user_id,
                                      message_id=call.message.message_id,
                                      reply_markup=button.choose_product_count('increment',actual_count))
    elif call.data == 'decrement':
        actual_count = users[user_id]['pr_count']
        users[user_id]['pr_count'] -= 1
        bot.edit_message_reply_markup(chat_id=user_id,
                                      message_id=call.message.message_id,
                                      reply_markup=button.choose_product_count('decrement',actual_count))
    elif call.data == 'back':
        products = database.get_pr_name_id()
        bot.edit_message_text('Выберете пункт меню',
                              user_id
                              ,call.message.message_id,
                              reply_markup=button.main_menu_kb(products))

    elif call.data == 'add_to_cart':
        product_count = users[user_id]['pr_count']
        user_product = users[user_id]['pr_name']
        database.add_product(user_id,user_product,product_count)
        products = database.get_pr_name_id()
        bot.edit_message_text('Продукт добавлен в корзину',user_id,call.message.message_id,reply_markup=button.main_menu_kb(products))
@bot.callback_query_handler(lambda call: call.data in ['order','cart','clear_cart'])
def main_menu_handle(call):
    user_id = call.message.chat.id
    user_cart = database.get_exect_korzina(user_id)
    message_id = call.message.message_id
    if call.data == 'order':
        bot.delete_message(user_id,message_id)
        bot.send_message(user_id,'Отправьте локацию',reply_markup=button.location_kb())
        bot.register_next_step_handler(call.message, get_location)
    elif call.data == 'cart':
        user_cart = database.get_exect_korzina(user_id)
        # формируем сообщение со всеми данными
        full_text = 'Ваша корзина:\n\n'
        total_amount = 0
        for i in user_cart:
            full_text += f'{i[0]} x {i[1]} = {i[2]}\n'
            total_amount += i[2]

        full_text += f'\nИтог: {total_amount}'
        bot.edit_message_text(full_text,
                              user_id,
                              message_id,
                              reply_markup=button.get_cart_kb())

    elif call.data == 'clear_cart':
#вызов функции очистки
        database.delete_kor(user_id)
        bot.edit_message_text('Ваша корзина очищена',
                              user_id,
                              message_id,
                              reply_markup=button.main_menu_kb(database.get_pr_name_id()))
def get_location(message):
    user_id = message.from_user.id
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        address = geolocator.reverse((latitude,longitude))
        user_cart = database.get_exect_korzina(user_id)
        # формируем сообщение со всеми данными
        full_text = 'Ваш заказ:\n\n'
        user_info = database.get_user_number_name(user_id)
        full_text += f'Имя: {user_info[0]}\nНомер телефона: {user_info[1]}\n\n'
        total_amount = 0
        for i in user_cart:
            full_text += f'{i[0]} x {i[1]} = {i[2]}\n'
            total_amount += i[2]

        full_text+=f'\nИтог: {total_amount}\nАдрес: {address}'
        bot.send_message(user_id,full_text,reply_markup=button.get_accept_kb())
        bot.register_next_step_handler(message,get_accept, address,full_text)
def get_accept(message,address,full_text):
    user_id = message.from_user.id
    products = database.get_pr_name_id()
    if message.text == 'Подтвердить':
        # очистить корзину
        database.delete_kor(user_id)
        # отправим админу сообщение о новом заказе
        bot.send_message(291384604,full_text.replace('Ваш','Новый'))
        bot.send_message(user_id,f'Вы подтвердили заказ на {address} адрес',reply_markup=ReplyKeyboardRemove())

    elif message.text == 'Отменить':
        bot.send_message(user_id,'Вы отменили заказ',reply_markup=ReplyKeyboardRemove())

    bot.send_message(user_id,'Меню',reply_markup=button.main_menu_kb(products))

@bot.callback_query_handler(lambda call: int(call.data) in database.get_pr_id())
def get_user_product(call):
    user_id = call.message.chat.id
    users[user_id]={'pr_name':call.data, 'pr_count': 1}
    message_id = call.message.message_id
#     поменять кнопки на выбор
    bot.edit_message_text('Выберите количество', chat_id=user_id, message_id=message_id ,reply_markup=button.choose_product_count())

bot.polling(non_stop=True)
