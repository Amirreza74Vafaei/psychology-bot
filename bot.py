import os
import telebot
from flask import Flask, request

# مقدار مستقیم برای اجرا در لوکال
TOKEN = os.getenv("7946365837:AAGxQxkglL6awKfznD0K9OG6To163jWBm4M", "توکن_ربات_خود")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app-name.up.railway.app")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ذخیره‌سازی موقت کاربران
user_data = {}

# سوالات تست روانشناسی کلی
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

# گزینه‌ها و امتیاز هر گزینه
options = ["هیچ‌وقت", "گاهی", "اغلب", "تقریباً همیشه"]
scores = {"هیچ‌وقت": 0, "گاهی": 1, "اغلب": 2, "تقریباً همیشه": 3}

# شروع تست
@bot.message_handler(commands=["start"])
def start(message):
    user_data[message.chat.id] = {"responses": [], "index": 0}
    bot.send_message(message.chat.id, "سلام! تست روانشناسی کلی شروع شد. لطفاً به هر سوال با دقت پاسخ دهید.")
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
        analyze(chat_id)

# ذخیره پاسخ‌ها
def save_answer(message):
    user_data[message.chat.id]["responses"].append(message.text)
    user_data[message.chat.id]["index"] += 1
    ask_question(message.chat.id)

# تحلیل نهایی
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

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# ثبت webhook
@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

# اجرای سرور Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

# اجرای Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
