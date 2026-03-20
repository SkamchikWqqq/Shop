import os
import requests
from flask import Flask
from threading import Thread
import telegram
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

app = Flask('')

@app.route('/')
def home():
    return "✅ Я онлайн!"

def run():
    port = int(os.environ.get("PORT", 8080))  # Получаем порт из переменной окружения
    app.run(host='0.0.0.0', port=port)  # Запускаем Flask на этом порту

Thread(target=run).start()

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
async def start(message: types.Message):
    await message.reply('Привет! Я онлайн.')

# Функция для обработки нажатий на кнопки
async def button(callback_query: CallbackQuery):
    query = callback_query
    await query.answer()
    
    if query.data == 'catalog':
        keyboard = [
            [InlineKeyboardButton("pрoб1v", callback_data='pрoб1v')],
            [InlineKeyboardButton("zн0с3рр", callback_data='zн0с3рр')],
            [InlineKeyboardButton("Обучение", callback_data='training')],
            [InlineKeyboardButton("Разное", callback_data='misc')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите категорию:", reply_markup=reply_markup)

# Функция для обработки выбранного товара и отправки ссылки на оплату с изображением
async def process_payment(callback_query: CallbackQuery):
    query = callback_query
    await query.answer()

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
    await bot.send_photo(
        chat_id=query.message.chat.id,  # ID чата
        photo=open(image_path, 'rb'),  # Открываем локальное изображение
        caption=f"Вы выбрали товар: {product}\n"
                f"Цена: {usd_price}$\n"
                f"Перейдите по ссылке для оплаты: {payment_link}\n"
                "После оплаты напишите создателю @cunpar для получения товара."
    )

# Установка Webhook для вашего бота
# Убедитесь, что у вас правильно настроены webhook и сервер доступен для внешнего мира
# Для этого вам нужно будет настроить сервер, что выходит за пределы этого примера

async def main():
    # Создаем экземпляр Dispatcher
    from aiogram import Dispatcher
    dp = Dispatcher(bot)

    # Регистрируем обработчики команд
    dp.register_message_handler(start, commands=["start"])
    dp.register_callback_query_handler(button)
    dp.register_callback_query_handler(process_payment, pattern='.*')

    # Запуск polling для бота
    await dp.start_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

    # Запуск Flask-приложения на порту 8080
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))  # Запуск Flask
