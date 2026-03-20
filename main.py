import os
from flask import Flask
from threading import Thread

# Создаем экземпляр Flask-приложения
app = Flask('')

@app.route('/')
def home():
    return "✅ Я онлайн!"  # Ответ для UptimeRobot и других сервисов мониторинга

def run():
    port = int(os.environ.get("PORT", 8080))  # Получаем порт из переменной окружения
    app.run(host='0.0.0.0', port=port)  # Запускаем Flask на этом порту

Thread(target=run).start()  # Запуск Flask в отдельном потоке

# Теперь Telegram-бот
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# API ключи для вашего крипто бота
api_key = '553441:AAd905Dra8Qp1GdSHuBbnWJNj8DfZYIXljf'  # API хеш для крипто бота
bot_token = '8798655968:AAEGVzmu2RPbI2z6UqBeuUjZQWkTuWbzGqM'  # Токен вашего бота
admin_id = 130231824  # ID администратора

# URL для запросов к крипто боту
crypto_api_url = 'https://your_crypto_bot_api_url_here.com/api'  # Укажите URL вашего крипто бота API

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
        'key': api_key,
        'format': 'json',
        'amount': amount,
        'currency1': 'USD',  # Базовая валюта для расчета
        'currency2': currency,  # Криптовалюта для оплаты
        'buyer_email': 'buyer@example.com',
        'item_name': f"Товар для заказа {order_id}",
        'item_number': order_id,
        'success_url': f'https://t.me/{bot_token}?start=success_{order_id}',
        'cancel_url': f'https://t.me/{bot_token}?start=cancel_{order_id}',
    }

    # Запрос к API крипто бота
    response = requests.post(crypto_api_url, data=data)
    response_json = response.json()

    if response_json.get('error') == 'ok':
        payment_url = response_json['result']['payment_url']
        return payment_url
    else:
        return f"Ошибка: {response_json.get('error')}"

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

# Функция для старта бота
def start(update, context):
    user = update.message.from_user
    if user.id == admin_id:
        keyboard = [
            [InlineKeyboardButton("Каталог", callback_data='catalog')],
            [InlineKeyboardButton("Профиль", callback_data='profile')],
            [InlineKeyboardButton("Реферальная система", callback_data='referral')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Главное меню магазина', reply_markup=reply_markup)

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

    elif query.data == 'pрoб1v':
        keyboard = [
            [InlineKeyboardButton("Пробив по юзернейму - 3$", callback_data='pрoб1v_user_3')],
            [InlineKeyboardButton("Пак моих тулок и софтов - 8$", callback_data='pроb1v_tools_8')],
            [InlineKeyboardButton("Премиум обучения - 16$", callback_data='pрoб1v_premium_16')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Выберите товар:", reply_markup=reply_markup)

    elif query.data == 'zн0с3рр':
        keyboard = [
            [InlineKeyboardButton("Базовый zн0с3рр - 4$", callback_data='zн0с3рр_basic_4')],
            [InlineKeyboardButton("Кастом zн0с3рр - 10$", callback_data='zн0с3рр_custom_10')],
            [InlineKeyboardButton("Мой личный zн0с3рр - 12$", callback_data='zн0с3рр_personal_12')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Выберите товар:", reply_markup=reply_markup)

    elif query.data == 'training':
        keyboard = [
            [InlineKeyboardButton("Базовое обучение - 4$", callback_data='training_basic_4')],
            [InlineKeyboardButton("Полное обучение - 5$", callback_data='training_full_5')],
            [InlineKeyboardButton("Вип обучение - 20$", callback_data='training_vip_20')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Выберите обучение:", reply_markup=reply_markup)

    elif query.data == 'misc':
        keyboard = [
            [InlineKeyboardButton("Создать телеграм бота - 6$", callback_data='misc_bot_6')],
            [InlineKeyboardButton("Дефф от @cunpar - 8$", callback_data='misc_deff_8')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Выберите товар:", reply_markup=reply_markup)

# Запуск бота
def main():
    updater = Updater(bot_token, use_context=True)

    # Получаем диспетчер для добавления обработчиков
    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CallbackQueryHandler(process_payment, pattern='.*'))

    # Начинаем работать с ботом
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()