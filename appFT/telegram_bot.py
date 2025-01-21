import requests
import time

bot_token = '5724647176:AAEuC1p7C-emm_-TkfKvdtPuR5y3yTH5kbE'
admin_chat_id = '526973879'  # Ваш chat_id
subscribed_users = set()  # Множество для хранения ID чатов подписанных пользователей
sent_welcome_message_chats = set()  # Множество для хранения ID чатов, которым уже отправили приветствие
user_status = {}  # Словарь для хранения статусов пользователей
user_requests = {}  # Словарь для хранения истории запросов пользователей
last_update_id = None  # Для отслеживания последнего обработанного обновления

# Функция отправки сообщений админу
def send_message_to_admin(message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': admin_chat_id,
        'text': message,
    }
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки сообщения админу: {e}")
        return None

# Функция отправки сообщений пользователю
def send_message_to_user(chat_id, message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка отправки сообщения пользователю: {e}")

# Функция для отправки приветственного сообщения пользователю
def send_welcome_message(chat_id):
    message = "Привет! Если у тебя есть проблема или вопрос, напиши мне!"
    send_message_to_user(chat_id, message)
    user_status[chat_id] = "Новый запрос"  # Устанавливаем начальный статус
    user_requests[chat_id] = []  # Инициализируем список запросов пользователя

# Функция для обработки статуса запроса
def get_user_status(chat_id):
    return user_status.get(chat_id, "Статус не найден")

# Функция для добавления запроса пользователя
def add_user_request(chat_id, request_text):
    if chat_id not in user_requests:
        user_requests[chat_id] = []
    user_requests[chat_id].append(request_text)

# Функция для получения всех запросов пользователя
def get_user_requests(chat_id):
    requests = user_requests.get(chat_id, [])
    if not requests:
        return "У вас нет запросов."
    return "\n".join(f"{i + 1}. {request}" for i, request in enumerate(requests))

# Функция для обработки сообщений от пользователя
def handle_message(update):
    chat_id = update['message']['chat']['id']
    text = update['message'].get('text', '')

    # Добавление пользователя в список подписанных пользователей, если он использует /start
    if text == '/start' and chat_id not in sent_welcome_message_chats:
        send_welcome_message(chat_id)
        sent_welcome_message_chats.add(chat_id)  # Добавляем в множество, чтобы больше не отправлять
        subscribed_users.add(chat_id)  # Добавляем пользователя в список подписанных пользователей

    # Обработка команды /status для получения статуса пользователя
    elif text.lower() == '/status':
        user_status_message = get_user_status(chat_id)
        send_message_to_user(chat_id, f"Ваш текущий статус: {user_status_message}")

    # Обработка команды /requests для получения всех запросов пользователя
    elif text.lower() == '/requests':
        user_requests_message = get_user_requests(chat_id)
        send_message_to_user(chat_id, f"Ваши запросы:\n{user_requests_message}")

    # Обработка проблемы пользователя
    elif text.lower().startswith('проблема'):
        # Устанавливаем статус "Обрабатывается" для пользователя
        user_status[chat_id] = "Обрабатывается"
        add_user_request(chat_id, text)  # Добавляем запрос в историю
        send_message_to_admin(f"Проблема от пользователя {chat_id}: {text}")
        response_message = "Спасибо за ваше сообщение! Мы с вами свяжемся."
        send_message_to_user(chat_id, response_message)
    
    # Обработка команды /ответ
    elif text.startswith('/ответ'):
        # Проверка, что сообщение отправил админ
        if chat_id == int(admin_chat_id):
            parts = text.split(' ', 2)
            if len(parts) == 3:
                target_chat_id = parts[1]  # ID чата пользователя
                response_text = parts[2]  # Текст ответа
                send_message_to_user(target_chat_id, response_text)
                send_message_to_admin(f"Ответ отправлен пользователю {target_chat_id}: {response_text}")
            else:
                send_message_to_admin("Неверный формат команды /ответ. Используйте: /ответ <chat_id> <текст ответа>")

    # Ответ на сообщение
    elif text:
        send_message_to_admin(f"Сообщение от пользователя {chat_id}: {text}")
        response_message = "Спасибо за ваше сообщение! Мы с вами свяжемся."
        send_message_to_user(chat_id, response_message)

# Пример получения обновлений от бота
def get_updates():
    global last_update_id
    url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
    
    # Если last_update_id существует, передаем его, чтобы начать получать обновления с последнего ID
    params = {}
    if last_update_id:
        params['offset'] = last_update_id + 1
    
    try:
        response = requests.get(url, params=params)
        updates = response.json()

        # Обработка каждого обновления
        for update in updates['result']:
            handle_message(update)
            last_update_id = update['update_id']  # Обновляем последний обработанный ID
    except Exception as e:
        print(f"Ошибка получения обновлений: {e}")

# Запускаем цикл получения сообщений
while True:
    get_updates()  # функция, которая обрабатывает обновления
    time.sleep(2)  # Пауза между запросами (не более 1 раз в 2 секунды)