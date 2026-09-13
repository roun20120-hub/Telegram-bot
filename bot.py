import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime
import pytz

# បង្កើត Web Server តូចមួយសម្រាប់ Keep-Alive
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# --- កូដ Telegram Bot ---
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ជម្រាបសួរ! ខ្ញុំជា Bot រំលឹកការងារ។ ប្រើបញ្ជា `/set HH:MM សារ` ដើម្បីកំណត់ម៉ោងរំលឹក។")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=f"⏰ រំលឹក៖ {job.data}")

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args or len(context.args) < 1:
            await update.message.reply_text("❌ សូមបញ្ចូលម៉ោង! ឧទាហរណ៍៖ `/set 11:00 ដល់ពេលរៀន`", parse_mode='Markdown')
            return

        time_str = context.args[0]
        message = " ".join(context.args[1:]) if len(context.args) > 1 else "ដល់ពេលត្រូវធ្វើការងារហើយ!"

        time_parts = time_str.split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])

        # កំណត់ Timezone Cambodia សម្រាប់ Time Object
        cambodia_tz = pytz.timezone('Asia/Phnom_Penh')
        target_time = datetime.time(hour=hours, minute=minutes, tzinfo=cambodia_tz)

        context.job_queue.run_daily(
            send_reminder,
            time=target_time,
            chat_id=update.effective_chat.id,
            data=message
        )

        await update.message.reply_text(f"✅ បានកំណត់ការរំលឹកនៅម៉ោង **{time_str}** រៀងរាល់ថ្ងៃ!\nសារ៖ {message}", parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ កើតមានបញ្ហា Error: `{str(e)}`", parse_mode='Markdown')

if __name__ == '__main__':
    # រត់ Web Server លើ Thread ដាច់ដោយឡែក
    threading.Thread(target=run_flask, daemon=True).start()

    # បង្កើត Application ដោយគ្មាន `.timezone()`
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(30)
        .connect_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set", set_timer))

    print("Bot កំពុងដំណើរការ...")
    app.run_polling(drop_pending_updates=True)