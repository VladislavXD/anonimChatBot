from telebot import TeleBot
from telebot import types
from config import TOKEN
from database import Database
from user import User
from config import ADMINID
import os
from keep_alive import keep_alive
user = User("db.db")
db = Database("db.db")

bot = TeleBot(os.environ.get('TOKEN'))

total_users = 0
total_messages = 0
users = set()

keep_alive()

def analitycs(func):
    def analytics_wrapper(message):
        global total_users, total_messages, users
        
        # Increment total messages
        total_messages += 1
        
        # Add unique user to the set and increment total users
        if message.chat.id not in users:
            users.add(message.chat.id)
            total_users += 1
        
        # Execute the decorated function
        func(message)
        
        # If the message is from admin, send analytics
            

            
    
    return analytics_wrapper


# Комманды -----------------------------------------------------------------------------------

@bot.message_handler(commands=['help'])
@analitycs
def help(message):
    bot.send_message(message.chat.id, """
Анонимный чат бот найдет собеседника для анонимного общения по интересам и полу.

Доступные команды:

/profile - посмотреть или изменить профиль
/rules - правила общения в чатах 
/menu - Главное меню
/help - Справка

/search - поиск собеседника - следующий собеседник
/stop - закончить диалог


Все команды всегда доступны по кнопке «Меню» в левой нижней части экрана

В чатах ты можешь отправлять мне текст( ссылки, гифки, стикеры, фотографии, видео или голосовые сообщения --- скоро) и я их анонимно перешлю твоему собеседнику.""")
    
@bot.message_handler(commands=['rules'])
@analitycs
def rules(message):
    bot.send_message(message.chat.id, 'Скоро')
    
@bot.message_handler(commands=['start'])
@analitycs
def register(message):
    
    
    if (not db.user_exsist(message.chat.id)):
        db.add_user(message.chat.id)
        send_gender_selection(message.chat.id)
    else:
        send_welcome(message)
        


def send_gender_selection(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("Мужской", callback_data="male"),
    types.InlineKeyboardButton("Женский", callback_data="female"))
    
    bot.send_message(chat_id, '📝 Регистрация\n👣 Шаг 1 из 4\n\nВыбери ниже, какого ты пола?', reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data in ["male", "female"])
def handle_gender(call):
    gender = "Мужской" if call.data == "male" else "Женский"
    chat_id = call.message.chat.id
    
    if db.get_signup(chat_id) == 'setgender':
        db.set_gender(chat_id, gender)
        db.set_signup(chat_id, "room")
        
        send_room_selection(chat_id)

def send_room_selection(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.row(types.InlineKeyboardButton("Общение", callback_data="communication"),
               types.InlineKeyboardButton("Знакомства", callback_data="acquaintance"),
               types.InlineKeyboardButton("Ищу Друга", callback_data="friend"))
    
    bot.send_message(chat_id, '👥 Выберите цель посещения бота:', reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data in ["communication", "acquaintance", "friend"])
def handle_room(call):
    chat_id = call.message.chat.id
    room = {
        "communication": "Общение",
        "acquaintance": "Знакомства",
        "friend": "Ищу Друга"
    }[call.data]
    if db.get_signup(chat_id) == "room":
        db.set_room(chat_id, room)
        db.set_signup(chat_id, "age")
        
         # Теперь нужно запросить возраст
        ask_for_age(chat_id)



def ask_for_age(chat_id):
    msg = bot.send_message(chat_id, '🎂 Шаг 3 из 4\n\nВведите свой возраст:')
    bot.register_next_step_handler(msg, handle_age_input)

   

def handle_age_input(message):
    chat_id = message.chat.id
    try:
        age = int(message.text)
        if age <= 0:
            raise ValueError("Возраст должен быть положительным числом")
        
        db.set_age(chat_id, age)
        db.set_signup(chat_id, "done")
        
        bot.send_message(chat_id, 'Регистрация завершена. Добро пожаловать!')
        send_welcome(message)
    
    except ValueError as e:
        bot.send_message(chat_id, 'Некорректный возраст. Пожалуйста, введите целое положительное число.')
        ask_for_age(chat_id)




def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item1 = types.KeyboardButton('🔎 Поиск собеседника')  
    item2 = types.KeyboardButton('👤 Профиль')  

    markup.add(item1, item2)
    
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}! Добро пожалывать в анонимный чат, нажми на поиск собеседника', reply_markup=markup)
    
    

@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item1 = types.KeyboardButton('🔎 Поиск собеседника')   
    item2 = types.KeyboardButton('👤 Профиль')   
    markup.add(item1, item2)
    
    bot.send_message(message.chat.id, 'Меню'.format(message.from_user), reply_markup=markup)
   
   
@bot.message_handler(commands=['profile'])
@analitycs
def profile(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item1 = types.KeyboardButton('🔎 Поиск собеседника')  
    item2 = types.KeyboardButton('👤 Профиль')    
    markup.add(item1, item2)
    markup2 = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('Изменить пол', callback_data='edit_gender')
    btn2 = types.InlineKeyboardButton('Изменить Возраст', callback_data='edit_age')
    markup2.add(btn1, btn2)
    
    user_data = f"""
🆔 ID: {message.chat.id}\n\n
👤 Имя -- {message.from_user.first_name}\n
🌌 Пол -- {user.get_gender(message.chat.id)}\n  
🚪 Комната -- {user.get_room(message.chat.id)}\n
🔞 Возраст -- {user.get_age(message.chat.id)} лет
    """
    bot.send_message(message.chat.id, user_data, reply_markup=markup2)
    
    # Inline buttons for editing gender and age


@bot.callback_query_handler(func=lambda call: call.data in ["edit_gender", "edit_age"])
def handle_edit_profile(call):
    chat_id = call.message.chat.id
    
    if call.data == "edit_gender":
        change_gender(call.message)
    
    elif call.data == "edit_age":
        # Prompt the user to input new age
        bot.send_message(chat_id, "Введите ваш новый возраст:")
        bot.register_next_step_handler(call.message, handle_new_age)

def change_gender(message):
    chat_id = message.chat.id

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('Назад', callback_data='back')
    btn2 = types.InlineKeyboardButton("Мужской", callback_data="male")
    btn3 = types.InlineKeyboardButton("Женский", callback_data="female")

    markup.add(btn3, btn2, btn1)  # Используем списки для формирования кнопок в разметке

    bot.edit_message_text("Данные пункт в разработке", chat_id=chat_id, message_id=message.message_id, reply_markup=markup)

# в разработке
@bot.callback_query_handler(func=lambda call: call.data in ["male", "female", 'back'])
def new_gender(call):
    if call.data == 'back': 
        bot.delete_message(call.message.chat.id, call.message.message_id)
        profile(call.message)

    # gender = "Мужской" if call.data == "male" else "Женский"
    # chat_id = call.message.chat.id
    

    # db.set_gender(chat_id, gender)

    
    # profile(chat_id)

def handle_new_age(message):
    chat_id = message.chat.id
    try:
        new_age = int(message.text.strip())
        if new_age > 0:
            user.set_age(chat_id, new_age)
            bot.send_message(chat_id, f"Возраст успешно изменен на {new_age} лет")
            profile(message)
        else:
            bot.send_message(chat_id, "Введите корректный возраст (положительное число)")
    except ValueError:
        bot.send_message(chat_id, "Введите корректный возраст (целое число)")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка при обновлении возраста: {str(e)}")

   
@bot.message_handler(commands=['stop'])
@analitycs
def stop(message): 
    chat_info = db.get_active_chat(message.chat.id)
    # Завершение поиска в случае если юзер был в поиске
    if db.is_in_queue(message.chat.id):
        markup3 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item3 = types.KeyboardButton('🔎 Поиск собеседника')   
        item4 = types.KeyboardButton('👤 Профиль')    
        markup3.add(item3, item4)
        
        db.delete_queue(message.chat.id)
        bot.send_message(message.chat.id, '❌ Вы завершили поиск', reply_markup=markup3 )
 
    # Завершаем чат с юзером и удаляем
    elif chat_info != False:
        db.delete_chat(chat_info[0])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Меню')   
        markup.add(item1)
        
        bot.send_message(chat_info[1], 'Собеседник чакинул пат, нажмите /menu', reply_markup=markup)
        bot.send_message(message.chat.id, 'Вы чакинули пат, нажмите /menu', reply_markup=markup)
    
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Меню')   
        markup.add(item1)
        bot.send_message(message.chat.id, 'Вы не начали общение> /menu', reply_markup=markup)
        
    
@bot.message_handler(commands=['search'])
@analitycs
def search(message):
    if message.chat.type == 'private':

        if db.is_in_queue(message.chat.id):
            bot.send_message(message.chat.id, '🔎 Идет поиск собеседника')
            return

            
        chat_info = db.get_active_chat(message.chat.id) 
        if chat_info != False:
            # следующий поик собеседника в случае нажатие с уже существующем диалогом
            db.delete_chat(chat_info[0])
            bot.send_message(chat_info[1], 'Собеседник чакинул пат, нажмите ')
            bot.send_message(message.chat.id, 'Вы чакинули пат, нажмите ')
                    
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('❌ Остановить поиск')   
        markup.add(item1)
        
        chat_two = db.get_chat()
        
        # добавляем в очередь
        if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id)
                bot.send_message(message.chat.id, '👤 Поиск собеседника', reply_markup=markup)
        else:
                # юзер нашлся, создаем чат
                markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton('/stop')   
                markup2.add(item1)
                
                mess = "Собеседник найден! \nследующий собеседник: /search \nЗавершить диалог: /stop"
                bot.send_message(message.chat.id, mess, reply_markup=markup2)
                bot.send_message(chat_two, mess, reply_markup=markup2)
    
   

    
    



# Работа с текстовыми коммандами и обработка текста :D ----------------------
@bot.message_handler(content_types=['text'])
@analitycs
def chat_message(message):
    bot.send_message(ADMINID, f"Analytics:\nUser: {message.from_user.first_name}\nMessage: {message.text}\nTotal Messages: {total_messages}\nTotal Users: {total_users}" )
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        
        if message.text == '👤 Профиль':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            item1 = types.KeyboardButton('🔎 Поиск собеседника')  
            item2 = types.KeyboardButton('👤 Профиль')    
            markup.add(item1, item2)
            
            markup2 = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton('Изменить пол', callback_data='edit_gender')
            btn2 = types.InlineKeyboardButton('Изменить Возраст', callback_data='edit_age')
            markup2.add(btn1, btn2)
            
            user_data = f"""
🆔 ID: {message.chat.id}\n\n
👤 Имя -- {message.from_user.first_name}\n
🌌 Пол -- {user.get_gender(message.chat.id)}\n
🚪 Комната -- {user.get_room(message.chat.id)}\n
🔞 Возраст -- {user.get_age(message.chat.id)} лет
            """
            bot.send_message(message.chat.id, user_data, reply_markup=markup2 )
            
            
        
        
        elif message.text == '🔎 Поиск собеседника':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('❌ Остановить поиск')   
            markup.add(item1)
            
            
            chat_two = db.get_chat()
            
            # добавляем в очередь
            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id)
                bot.send_message(message.chat.id, '👤 Поиск собеседника', reply_markup=markup)
            else:
                # юзер нашлся, создаем чат
                markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton('/stop')   
                markup2.add(item1)
                
                mess = "Собеседник найден! \nследующий собеседник: /search \nЗавершить диалог: /stop"
                bot.send_message(message.chat.id, mess, reply_markup=markup2)
                bot.send_message(chat_two, mess, reply_markup=markup2)
            
        # остановка поиска собеседника
        elif message.text == '❌ Остановить поиск':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            item1 = types.KeyboardButton('🔎 Поиск собеседника')  
            item2 = types.KeyboardButton('👤 Профиль')    
            markup.add(item1, item2)
            
            db.delete_queue(message.chat.id)
            bot.send_message(message.chat.id, '❌ Поиск остановлен', reply_markup=markup)
        elif chat_info == False:
            bot.send_message(message.chat.id, 'Вы не начали диалог')
            
        else:
            chat_info = db.get_active_chat(message.chat.id)
            bot.send_message(chat_info[1], message.text)
    

    
 

bot.polling(none_stop=True)
