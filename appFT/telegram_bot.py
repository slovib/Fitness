import telebot
import psycopg2
from datetime import datetime, timedelta

# Токен бота и ID админа
bot_token = '5724647176:AAEuC1p7C-emm_-TkfKvdtPuR5y3yTH5kbE'
admin_chat_id = '526973879'

bot = telebot.TeleBot(bot_token)

def connect_db():
    try:
        return psycopg2.connect(
            dbname="ll",
            user="postgres",
            password="123",
            host="localhost",
            port="5433"
        )
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

def create_table():
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS message_user (
                        user_id BIGINT PRIMARY KEY,
                        message TEXT,
                        admin_reply TEXT DEFAULT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")
        finally:
            conn.close()

def delete_old_messages():
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cutoff_date = datetime.now() - timedelta(days=10)
                cursor.execute("DELETE FROM message_user WHERE timestamp < %s;", (cutoff_date,))
                conn.commit()
        except Exception as e:
            print(f"Ошибка при удалении старых сообщений: {e}")
        finally:
            conn.close()

def save_message_to_db(user_id, message, admin_reply=None):
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO message_user (user_id, message, admin_reply)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE 
                    SET message = EXCLUDED.message, admin_reply = EXCLUDED.admin_reply, timestamp = CURRENT_TIMESTAMP;
                """, (user_id, message, admin_reply))
                conn.commit()
        except Exception as e:
            print(f"Ошибка при сохранении сообщения: {e}")
        finally:
            conn.close()

def get_message_from_db(user_id):
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT message, admin_reply FROM message_user WHERE user_id = %s;", (user_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка при получении сообщения: {e}")
        finally:
            conn.close()
    return None

def get_all_users():
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM message_user;")
                return [user[0] for user in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при извлечении пользователей: {e}")
        finally:
            conn.close()
    return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! 👋 Напиши свою проблему, и мы рассмотрим её в течение 10 часов. 🕒")

@bot.message_handler(func=lambda message: not message.text.startswith('\\ответ') and not message.text.startswith('/news'))
def handle_user_message(message):
    user_id = message.from_user.id
    user_message = message.text
    save_message_to_db(user_id, user_message)
    bot.reply_to(message, "Спасибо за ваше сообщение! 🙌 Мы рассмотрим вашу проблему в течение 10 часов. ⏳")
    bot.send_message(admin_chat_id, f"Новое сообщение от {user_id}: {user_message}")

@bot.message_handler(func=lambda message: message.text.startswith('\\ответ'))
def handle_admin_reply(message):
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        admin_reply = ' '.join(parts[2:])
        result = get_message_from_db(user_id)
        if result:
            user_message, current_admin_reply = result
            if not current_admin_reply:
                save_message_to_db(user_id, user_message, admin_reply)
                bot.send_message(user_id, f"Ответ от администратора: {admin_reply} 📩")
                bot.send_message(admin_chat_id, f"Ответ отправлен пользователю {user_id}. ✅")
            else:
                bot.send_message(admin_chat_id, f"Администратор уже ответил пользователю {user_id}. ❌")
        else:
            bot.send_message(admin_chat_id, f"Пользователь с ID {user_id} не найден. ❌")
    except Exception as e:
        bot.send_message(admin_chat_id, f"Ошибка при обработке ответа: {e} ❌")

@bot.message_handler(commands=['news'])
def send_news(message):
    if str(message.from_user.id) == admin_chat_id:
        news_text = ' '.join(message.text.split()[1:])
        if news_text:
            for user_id in get_all_users():
                try:
                    bot.send_message(user_id, f"📢 Новость: {news_text}")
                except Exception as e:
                    print(f"Не удалось отправить сообщение {user_id}: {e}")
            bot.send_message(admin_chat_id, "Новость успешно отправлена. ✅")
        else:
            bot.send_message(admin_chat_id, "Вы не указали текст новости. ❌")
    else:
        bot.reply_to(message, "У вас нет прав для этой команды. 🚫")

create_table()
delete_old_messages()
bot.polling(none_stop=True)
