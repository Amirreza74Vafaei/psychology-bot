import telebot
import time
import pandas as pd

# توکن ربات تلگرام شما
TOKEN = '7946365837:AAGxQxkglL6awKfznD0K9OG6To163jWBm4M'

# ایجاد شیء ربات
bot = telebot.TeleBot(TOKEN)

# سوالات روانشناسی با گزینه‌های متنوع‌تر
questions = [
    {"question": "چقدر احساس شادی می‌کنید؟", "options": ["بسیار زیاد", "زیاد", "متوسط", "کم", "بسیار کم"]},
    {"question": "آیا احساس استرس می‌کنید؟", "options": ["بله، خیلی زیاد", "بله، متوسط", "نه، کم", "نه، اصلاً"]},
    {"question": "آیا در روابط شخصی خود مشکل دارید؟", "options": ["بله، مشکلات شدید", "بله، مشکلات متوسط", "نه، مشکلات کم", "نه، هیچ مشکلی ندارم"]},
    {"question": "چه مدت در روز ورزش می‌کنید؟", "options": ["بیش از ۲ ساعت", "۱-۲ ساعت", "۳۰ دقیقه", "کمتر از ۳۰ دقیقه", "اصلاً ورزش نمی‌کنم"]},
    {"question": "آیا به طور منظم خواب کافی دارید؟", "options": ["بله، بیشتر از ۸ ساعت", "بله، ۶-۸ ساعت", "کمتر از ۶ ساعت", "اصلاً خواب کافی ندارم"]},
    {"question": "چقدر احساس اعتماد به نفس می‌کنید؟", "options": ["بسیار زیاد", "زیاد", "متوسط", "کم", "بسیار کم"]},
    {"question": "آیا در مواجهه با مشکلات زندگی احساس ضعف می‌کنید؟", "options": ["بله، همیشه", "بله، گاهی", "نه، کمی", "نه، اصلاً"]},
    {"question": "چقدر احساس تنهایی می‌کنید؟", "options": ["بسیار زیاد", "زیاد", "متوسط", "کم", "بسیار کم"]},
    {"question": "آیا احساس اضطراب می‌کنید؟", "options": ["بله، شدید", "بله، متوسط", "نه، کم", "نه، اصلاً"]},
    {"question": "آیا به طور منظم به خودتان استراحت می‌دهید؟", "options": ["بله، روزانه", "بله، هفتگی", "گاهی اوقات", "هرگز"]},
]

# لیست ذخیره پاسخ‌ها
answers = []

# فرمان برای شروع
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! به ربات تست روانشناسی خوش آمدید!")
    ask_question(message)

# تابع برای پرسیدن سوالات
def ask_question(message, index=0):
    if index < len(questions):
        question = questions[index]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for option in question["options"]:
            markup.add(option)
        bot.send_message(message.chat.id, question["question"], reply_markup=markup)
        bot.register_next_step_handler(message, process_answer, index)
    else:
        bot.send_message(message.chat.id, "تمام سوالات تمام شدند. در حال تجزیه و تحلیل نتایج شما...")
        # ایجاد فایل Excel و ارسال به کاربر
        save_results_to_excel(message.chat.id)
        # ارسال پیام نتیجه‌گیری
        send_results(message)
        answers.clear()  # پاک کردن پاسخ‌ها برای شروع جدید

# پردازش پاسخ‌ها
def process_answer(message, index):
    answers.append(message.text)
    ask_question(message, index + 1)

# ارسال نتیجه‌گیری به کاربر
def send_results(message):
    # تحلیل و نتیجه‌گیری
    result = "نتیجه‌گیری: بر اساس پاسخ‌های شما، به نظر می‌رسد که شما نیاز به بررسی بیشتر وضعیت روانی و جسمی خود دارید. توصیه می‌شود که با مشاور صحبت کنید."
    bot.send_message(message.chat.id, result)
    bot.send_message(message.chat.id, "در صورت تمایل، شما را به مشاور وصل می‌کنم. شماره تماس مشاور: 09000000000")

# ذخیره نتایج به فایل Excel
def save_results_to_excel(chat_id):
    # ایجاد DataFrame از پاسخ‌ها
    data = {'Question': [q["question"] for q in questions], 'Answer': answers}
    df = pd.DataFrame(data)
    
    # ذخیره فایل Excel
    filename = f"results_{chat_id}.xlsx"
    df.to_excel(filename, index=False)

    # ارسال فایل به کاربر
    with open(filename, 'rb') as file:
        bot.send_document(chat_id, file)

# فرمان برای دریافت پیام‌های متنی
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

# شروع Polling
def start_polling():
    print("Polling started...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # در صورت بروز خطا، 5 ثانیه صبر می‌کند و دوباره تلاش می‌کند

if __name__ == '__main__':
    start_polling()
