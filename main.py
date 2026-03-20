import os
from flask import Flask, request
from threading import Thread
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import requests

# Создаем экземпляр Flask-приложения
app = Flask('')

# URL Webhook для вашего сервера
WEBHOOK_URL = 'https://your-app-name.onrender.com/webhook'  # Замените на ваш реальный URL

@app.route('/')
def home():
    return "✅ Я онлайн!"  # Ответ для UptimeRobot и других сервисов мониторинга

def run():
    port = int(os.environ.get("PORT", 8080))  # Получаем порт из переменной окружения
    app.run(host='0.0.0.0', port=port)  # Запускаем Flask на этом порту

Thread(target=run).start()  # Запуск Flask в отдельном потоке

# Ваш Telegram-бот
TOKEN = '8798655968:AAEGVzmu2RPbI2z6UqBeuUjZQWkTuWbzGqM'
bot = telegram.Bot(token=TOKEN)

# Локальный путь к изображению, которое будет отправляться
image_path = 'image.png'  # Ваше локальное изображение

# Функция для получения текущего курса BTC к USD с API CoinGecko
def get_btc_to_usd():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    return data['bitcoin']['usd']

# Конвертируем цену из USD в BTC
def convert_usd_to_btc(usd_amount):
    btc_to_usd = get_btc_to_usd()  # Получаем курс BTC/USD
    btc_amount = usd_amount / btc_to_usd  # Переводим USD в BTC
    return btc_amount

# Функция для генерации ссылки на оплату
def create_payment_link(amount, currency, order_id):
    data = {
        'cmd': 'create_transaction',
        'key': '553441:AAd905Dra8Qp1GdSHuBbnWJNj8DfZYIXljf',  # API хеш для крипто бота
        'format': 'json',
        'amount': amount,
        'currency1': 'USD',  # Базовая валюта для расчета
        'currency2': currency,  # Криптовалюта для оплаты
        'buyer_email': 'buyer@example.com',
        'item_name': f"Товар для заказа {order_id}",
        'item_number': order_id,
        'success_url': f'https://t.me/{TOKEN}?start=success_{order_id}',
        'cancel_url': f'https://t.me/{TOKEN}?start=cancel_{order_id}',
    }

    # Запрос к API крипто бота
    response = requests.post('https://your_crypto_bot_api_url_here.com/api', data=data)
    response_json = response.json()

    if response_json.get('error') == 'ok':
        payment_url = response_json['result']['payment_url']
        return payment_url
    else:
        return f"Ошибка: {response_json.get('error')}"

# Функция для обработки команды /start
def start(update, context):
    update.message.reply_text('Привет! Я онлайн.')

# Функция для обработки нажатий на кнопки
def button(update, context):
    query = update.callback_query
    query.answer()
    
    if query.data == 'catalog':
        keyboard = [
            [InlineKeyboardButton("pрoб1v", callback_data='pрoб1v')],
            [InlineKeyboardButton("zн0с3рр", callback_data='zн0с3рр')],
            [InlineKeyboardButton("Обучение", callback_data='training')],
            [InlineKeyboardButton("Разное", callback_data='misc')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Выберите категорию:", reply_markup=reply_markup)

# Функция для обработки выбранного товара и отправки ссылки на оплату с изображением
def process_payment(update, context):
    query = update.callback_query
    query.answer()

    # Получаем название товара и цену в USD
    product = query.data.split('_')[0]  # Например 'pрoб1v_user'
    usd_price = int(query.data.split('_')[1])  # Например 3$ (в долларах)

    # Конвертируем цену в биткойны
    btc_price = convert_usd_to_btc(usd_price)

    # Создаем уникальный ID для заказа
    order_id = f'{product}_{usd_price}'

    # Создаем ссылку на оплату через крипто бота (например, BTC)
    payment_link = create_payment_link(btc_price, 'BTC', order_id)

    # Отправляем локальное изображение и ссылку на оплату
    context.bot.send_photo(
        chat_id=query.message.chat_id,  # ID чата
        photo=open(image_path, 'rb'),  # Открываем локальное изображение
        caption=f"Вы выбрали товар: {product}\n"
                f"Цена: {usd_price}$\n"
                f"Перейдите по ссылке для оплаты: {payment_link}\n"
                "После оплаты напишите создателю @cunpar для получения товара."
    )

# Установка Webhook для вашего бота
def set_webhook():
    bot.setWebhook(WEBHOOK_URL)

def main():
    global dispatcher
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Добавляем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CallbackQueryHandler(process_payment, pattern='.*'))

    # Устанавливаем Webhook
    set_webhook()

if __name__ == '__main__':
    main()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))  # Запуск Flask
