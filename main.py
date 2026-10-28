import os, random, threading
from flask import Flask
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Alive!"

user_games = {}
questions = [
    {"q": "Пойтахти Тоҷикистон?", "a": ["Душанбе", "Хуҷанд", "Бохтар"], "c": 0},
    {"q": "2+2*2 = ?", "a": ["6", "8", "4"], "c": 0},
]

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎮 Рақамро ёб", "🧠 Викторина")
    markup.add("✊ Санг-Коғаз-Қайчӣ")
    bot.send_message(m.chat.id, f"Салом {m.from_user.first_name}! Ман Бози интересний! Бозиро интихоб кун:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎮 Рақамро ёб")
def gn(m):
    n = random.randint(1,100)
    user_games[m.chat.id]=n
    bot.send_message(m.chat.id, "Ман рақам аз 1-100 фикр кардам, ёб!")

@bot.message_handler(func=lambda m: m.text == "🧠 Викторина")
def gq(m):
    q = random.choice(questions)
    user_games[f"q_{m.chat.id}"]=q
    markup = types.InlineKeyboardMarkup()
    for i,a in enumerate(q['a']):
        markup.add(types.InlineKeyboardButton(a, callback_data=f"q_{i}"))
    bot.send_message(m.chat.id, q['q'], reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "✊ Санг-Коғаз-Қайчӣ")
def gr(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✊", callback_data="r_rock"), types.InlineKeyboardButton("✋", callback_data="r_paper"), types.InlineKeyboardButton("✌️", callback_data="r_scissors"))
    bot.send_message(m.chat.id, "Интихоб кун:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    if call.data.startswith("q_"):
        q=user_games.get(f"q_{call.message.chat.id}")
        if q and int(call.data.split("_")[1])==q['c']:
            bot.send_message(call.message.chat.id, "✅ Офарин дуруст!")
        else:
            bot.send_message(call.message.chat.id, f"❌ Хато! Дуруст: {q['a'][q['c']]}")
    if call.data.startswith("r_"):
        ch=["rock","paper","scissors"]
        bc=random.choice(ch)
        uc=call.data.split("_")[1]
        if uc==bc: res="Мусовӣ 🤝"
        elif (uc=="rock" and bc=="scissors") or (uc=="paper" and bc=="rock") or (uc=="scissors" and bc=="paper"): res="Ту бурдӣ 🏆"
        else: res="Ман бурдам 😎"
        bot.send_message(call.message.chat.id, res)

@bot.message_handler(func=lambda m: m.chat.id in user_games)
def check(m):
    try:
        g=int(m.text)
        r=user_games[m.chat.id]
        if g<r: bot.reply_to(m, "Калонтар 📈")
        elif g>r: bot.reply_to(m, "Хурдтар 📉")
        else: 
            bot.reply_to(m, "Офарин ёфтӣ! 🎉")
            del user_games[m.chat.id]
    except: pass

def run_bot(): bot.infinity_polling()
def run_web():
    port=int(os.environ.get("PORT",10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_bot).start()
run_web()
