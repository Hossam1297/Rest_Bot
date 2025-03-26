import os
import sqlite3
import telebot
import requests
import re

# جلب التوكن من المتغير البيئي
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# التأكد من أن التوكن موجود
if not TOKEN:
    raise ValueError("⚠️ لم يتم العثور على التوكن في المتغيرات البيئية!")

# إنشاء كائن البوت
bot = telebot.TeleBot(TOKEN)

# إنشاء قاعدة البيانات SQLite
DB_NAME = "user_stats.db"

def create_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS stats (
                        chat_id INTEGER PRIMARY KEY,
                        total_requests INTEGER DEFAULT 0,
                        successful_requests INTEGER DEFAULT 0,
                        failed_requests INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# التحقق من صحة البريد الإلكتروني
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# إرسال طلب الريست
def send_reset_email(chat_id, email):
    url = 'https://i.instagram.com/api/v1/accounts/send_password_reset/'
    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }
    data = {"user_email": email}

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200 and '"status":"ok"' in response.text:
            bot.send_message(chat_id, f"✅ تم إرسال طلب إعادة التعيين إلى: {email}")
        else:
            bot.send_message(chat_id, "❌ فشل في إرسال الريست، تأكد من صحة البريد!")
    except:
        bot.send_message(chat_id, "❌ حدث خطأ أثناء المحاولة!")

# استقبال الأوامر
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 أهلاً بك! أرسل البريد الإلكتروني لاستعادة الحساب.")

@bot.message_handler(func=lambda message: True)
def process_request(message):
    email = message.text.strip()
    if is_valid_email(email):
        send_reset_email(message.chat.id, email)
    else:
        bot.send_message(message.chat.id, "⚠️ أدخل بريد إلكتروني صالح.")

# تشغيل قاعدة البيانات والبدء
create_db()
bot.polling(none_stop=True)
