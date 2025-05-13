import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("7946365837:AAGxQxkglL6awKfznD0K9OG6To163jWBm4M")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# حافظه ساده برای ذخیره داده‌ها
user_data = {}

# سوالات ساده برای تست (می‌تونی گسترشش بدی)
questions = [
    "در یک ماه گذشته چقدر احساس استرس داشته‌اید؟",
    "چقدر به آینده امیدوار هستید؟"
]
options = ["خیلی کم", "کم", "متوسط", "زیاد", "خیلی زیاد"]

# صفحه خوش‌آمدگویی
@bot.message_handler(commands=["start"])
def start(message):
    user_data[message.chat.id] = {"responses": [], "index": 0}
    bot.send_message(message.chat.id, "سلام! برای شروع ارزیابی روانشناسی آماده‌اید؟")
    ask_question(message.chat.id)

# پرسیدن سوال
def ask_question(chat_id):
    index = user_data[chat_id]["index"]
    if index < len(questions):
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for opt in options:
            markup.add(telebot.types.KeyboardButton(opt))
        msg = bot.send_message(chat_id, questions[index], reply_markup=markup)
        bot.register_next_step_handler(msg, lambda m: save_answer(m))
    else:
        bot.send_message(chat_id, "✅ ارزیابی کامل شد. ممنون از همکاری‌تون.")

# ذخیره پاسخ
def save_answer(message):
    data = user_data[message.chat.id]
    data["responses"].append(message.text)
    data["index"] += 1
    ask_question(message.chat.id)

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# تنظیم Webhook هنگام شروع
@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

# اجرای Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
