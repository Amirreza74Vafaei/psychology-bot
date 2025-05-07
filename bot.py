import telebot
import pandas as pd
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7946365837:AAGE0fKHva9HUybg1weseLLK22XH2C4Odfs"  # ← اینجا توکن خودت رو بذار
bot = telebot.TeleBot(TOKEN)

user_data = {}

questions_options = {
    "در یک ماه گذشته چقدر احساس استرس داشته‌اید؟": ["اصلاً ندارم", "کم", "متوسط", "زیاد", "خیلی زیاد"],
    "هنگام مواجهه با مشکلات، معمولاً چه احساسی دارید؟": ["آرام", "کمی مضطرب", "نگران", "خیلی مضطرب", "بسیار نگران"],
    "آیا برای مدیریت اضطراب، از روش‌های خاصی استفاده می‌کنید؟": ["اصلاً", "به ندرت", "گاهی اوقات", "معمولاً", "همیشه"],
    "در هفته گذشته، چند روز احساس بی‌حوصلگی داشته‌اید؟": ["هیچ روزی", "۱-۲ روز", "۳-۴ روز", "۵-۶ روز", "هر روز"],
    "چقدر به آینده امیدوار هستید؟": ["اصلاً امیدوار نیستم", "کم", "متوسط", "زیاد", "خیلی زیاد"],
    "چه‌قدر انگیزه برای انجام کارهای روزمره دارید؟": ["خیلی کم", "کم", "متوسط", "زیاد", "بسیار زیاد"],
    "چقدر از تعاملات اجتماعی خود لذت می‌برید؟": ["اصلاً", "کمی", "متوسط", "زیاد", "خیلی زیاد"],
    "در جمع‌های اجتماعی چقدر احساس راحتی دارید؟": ["بسیار راحت", "نسبتاً راحت", "متوسط", "کمی سخت", "بسیار سخت"],
    "آیا معمولاً نظرات خود را با اعتماد به نفس بیان می‌کنید؟": ["اصلاً", "کمی", "متوسط", "زیاد", "خیلی زیاد"],
    "صبح‌ها با چه سطحی از انرژی از خواب بیدار می‌شوید؟": ["خیلی کم", "کم", "متوسط", "زیاد", "بسیار زیاد"],
    "در روزهای سخت، چگونه با چالش‌ها روبه‌رو می‌شوید؟": ["خیلی ضعیف", "ضعیف", "متوسط", "خوب", "عالی"],
    "چقدر احساس آرامش درونی دارید؟": ["خیلی کم", "کم", "متوسط", "زیاد", "خیلی زیاد"],
    "کیفیت خواب شما چگونه است؟": ["عالی", "خوب", "متوسط", "ضعیف", "خیلی ضعیف"],
    "آیا احساس می‌کنید که زمان کافی برای استراحت دارید؟": ["اصلاً", "کم", "متوسط", "زیاد", "خیلی زیاد"],
    "چه‌قدر عادات سالم (ورزش، تغذیه مناسب) در زندگی شما نقش دارند؟": ["اصلاً", "کم", "متوسط", "زیاد", "خیلی زیاد"]
}

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🟢 شروع ارزیابی"))
    markup.add(KeyboardButton("🔄 ارزیابی مجدد"), KeyboardButton("📍 آدرس مرکز"))
    markup.add(KeyboardButton("ℹ️ راهنما"), KeyboardButton("📥 دریافت گزارش"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {"name": "", "phone": "", "responses": []}
    bot.send_message(message.chat.id, "سلام! خوش آمدید به سیستم ارزیابی روانشناسی 🌿", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "🟢 شروع ارزیابی")
def start_assessment(message):
    bot.send_message(message.chat.id, "لطفاً نام و نام خانوادگی خود را وارد کنید:")

@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]["name"] == "")
def get_name(message):
    user_data[message.chat.id]["name"] = message.text
    bot.send_message(message.chat.id, "لطفاً شماره تماس خود را وارد کنید:")

@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]["phone"] == "")
def get_phone(message):
    user_data[message.chat.id]["phone"] = message.text
    ask_question(message.chat.id, 0)

def ask_question(chat_id, index):
    questions = list(questions_options.keys())
    if index < len(questions):
        markup = ReplyKeyboardMarkup(one_time_keyboard=True)
        for option in questions_options[questions[index]]:
            markup.add(KeyboardButton(option))
        msg = bot.send_message(chat_id, questions[index], reply_markup=markup)
        bot.register_next_step_handler(msg, lambda message: store_response(message, index))
    else:
        save_data(chat_id)

def store_response(message, index):
    questions = list(questions_options.keys())
    user_data[message.chat.id]["responses"].append((questions[index], message.text))
    ask_question(message.chat.id, index + 1)

def save_data(chat_id):
    data = user_data[chat_id]
    filename = f"{data['name']}_report.xlsx"
    df = pd.DataFrame({
        "سوالات": [q for q, _ in data["responses"]],
        "پاسخ‌ها": [r for _, r in data["responses"]]
    })
    df.to_excel(filename, index=False, engine="openpyxl")
    with open(filename, "rb") as file:
        bot.send_document(chat_id, file)
    bot.send_message(chat_id, "✅ فایل گزارش ارسال شد!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "🔄 ارزیابی مجدد")
def restart_assessment(message):
    user_data[message.chat.id] = {"name": "", "phone": "", "responses": []}
    bot.send_message(message.chat.id, "🔄 لطفاً نام خود را وارد کنید:")

@bot.message_handler(func=lambda message: message.text == "📍 آدرس مرکز")
def center_address(message):
    bot.send_message(message.chat.id, "📍 تهران، خیابان …\n📞 تماس: 0912XXXXXXX")

@bot.message_handler(func=lambda message: message.text == "ℹ️ راهنما")
def help_message(message):
    bot.send_message(message.chat.id, "📘 راهنما: ابتدا شروع ارزیابی را بزنید و مراحل را دنبال کنید.")

@bot.message_handler(func=lambda message: message.text == "📥 دریافت گزارش")
def get_report(message):
    bot.send_message(message.chat.id, "📤 به زودی گزارش‌های شما ارسال می‌شود.")

bot.polling(non_stop=True)
