import os
from flask import Flask, request
import telebot

# 📌 دریافت توکن و URL از محیط (یا مقدار پیش‌فرض)
TOKEN = os.getenv("TOKEN", "7946365837:AAGxQxkglL6awKfznD0K9OG6To163jWBm4M")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://psychology-bot-production.up.railway.app/set_webhook")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

# ✅ سوالات تست روانشناسی
questions = [
    "در دو هفته گذشته، چقدر احساس بی‌قراری یا اضطراب داشته‌اید؟",
    "چقدر از فعالیت‌های روزمره لذت می‌برید؟",
    "آیا احساس ناامیدی نسبت به آینده دارید؟",
    "چه میزان اعتماد به نفس در برخورد با دیگران دارید؟",
    "در خوابیدن یا خواب ماندن، چقدر مشکل دارید؟",
    "در طول روز چند بار احساس خستگی مفرط داشته‌اید؟",
    "آیا افکار منفی تکراری ذهن‌تان را مشغول می‌کنند؟",
    "چقدر از بودن در جمع احساس ناراحتی می‌کنید؟",
    "در تصمیم‌گیری‌های ساده، چقدر دچار تردید می‌شوید؟",
    "احساس می‌کنید توانایی کنترل شرایط زندگی را دارید؟"
]

options = ["هیچ‌وقت", "گاهی", "اغلب", "تقریباً همیشه"]
scores = {"هیچ‌وقت": 0, "گاهی": 1, "اغلب": 2, "تقریباً همیشه": 3}

# 🎯 شروع تست
@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("شروع تست روانشناسی")
    bot.send_message(message.chat.id, "سلام! به ربات تست روانشناسی خوش آمدید. لطفاً گزینه زیر را برای شروع تست انتخاب کنید:", reply_markup=markup)

# 🎯 گزینه شروع تست
@bot.message_handler(func=lambda message: message.text == "شروع تست روانشناسی")
def start_test(message):
    user_data[message.chat.id] = {"responses": [], "index": 0}
    bot.send_message(message.chat.id, "تست روانشناسی شروع شد. لطفاً به هر سوال پاسخ دهید.")
    ask_question(message.chat.id)

# ❓ ارسال سوال
def ask_question(chat_id):
    index = user_data[chat_id]["index"]
    if index < len(questions):
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for opt in options:
            markup.add(opt)
        msg = bot.send_message(chat_id, questions[index], reply_markup=markup)
        bot.register_next_step_handler(msg, save_answer)
    else:
        analyze(chat_id)

# 📝 ذخیره پاسخ‌ها
def save_answer(message):
    chat_id = message.chat.id
    answer = message.text
    user_data[chat_id]["responses"].append(answer)
    user_data[chat_id]["index"] += 1
    ask_question(chat_id)

# 📊 تحلیل تست
def analyze(chat_id):
    responses = user_data[chat_id]["responses"]
    total_score = sum(scores.get(ans, 1) for ans in responses)

    if total_score <= 10:
        result = "🟢 وضعیت کلی روانی شما پایدار و خوب است."
    elif total_score <= 20:
        result = "🟠 برخی علائم خفیف دیده می‌شود. توصیه می‌شود سبک زندگی سالم‌تری اتخاذ کنید."
    else:
        result = (
            "🔴 نشانه‌هایی از اضطراب یا فشار روانی قابل توجه وجود دارد.\n"
            "توصیه می‌شود با مشاور صحبت کنید.\n"
            "📞 شماره مشاور: [در این قسمت قرار دهید]"
        )

    bot.send_message(chat_id, f"📊 تحلیل تست:\n{result}")

# 📬 وبهوک اصلی
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# 🔧 ست کردن وبهوک
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    return "Webhook set!", 200

# ⚙️ اجرای فقط در محیط توسعه
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
