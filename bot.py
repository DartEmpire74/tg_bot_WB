from dotenv import load_dotenv
import os
import telebot
from telebot import types
import pandas as pd

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)


def load_data():
    return pd.read_csv('sales.csv')


# --- КНОПКИ ---
def main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)

    btn1 = types.InlineKeyboardButton("💰 Выручка", callback_data='report')
    btn2 = types.InlineKeyboardButton("🏆 Топ товаров", callback_data='top')
    btn3 = types.InlineKeyboardButton("📦 Юнит экономика", callback_data='unit')

    markup.add(btn1, btn2, btn3)
    return markup


# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я бот аналитики продаж\n\nВыбери действие:",
        reply_markup=main_keyboard()
    )


# --- ОБРАБОТКА КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'report':
        send_report(call.message)

    elif call.data == 'top':
        send_top(call.message)

    elif call.data == 'unit':
        send_unit(call.message)


# --- ЛОГИКА ---
def send_report(message):
    df = load_data()
    revenue = (df['quantity'] * df['price']).sum()

    bot.send_message(
        message.chat.id,
        f"💰 Общая выручка: {revenue} ₽",
        reply_markup=main_keyboard()
    )


def send_top(message):
    df = load_data()

    df['revenue'] = df['quantity'] * df['price']
    top = df.groupby('product')['revenue'].sum().sort_values(ascending=False)

    text = "🏆 Топ товаров:\n\n"
    for product, revenue in top.head(5).items():
        text += f"{product}: {revenue} ₽\n"

    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())


def send_unit(message):
    df = load_data()

    df['profit'] = (df['price'] - df['cost']) * df['quantity']
    result = df.groupby('product')['profit'].sum()

    text = "📦 Юнит экономика:\n\n"
    for product, profit in result.items():
        text += f"{product}: {profit} ₽ прибыли\n"

    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())


# --- ЗАПУСК ---
bot.polling(none_stop=True)
