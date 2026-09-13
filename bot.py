import os
import logging
import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ស្រូបយក Token ពី Environment Variable (ឬប្រើ Token ថ្មីជា Default)
TOKEN = os.getenv("BOT_TOKEN", "8859001589:AAHhxe_7Xz9ETJO-psGIOxqrpW1oKrmyr64")

# បង្ហាញ Log ពេលមាន Error
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=job.data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ជម្រាបសួរ! ខ្ញុំជា Reminder Bot របស់អ្នក។\n\n"
        "របៀបប្រើប្រាស់៖\n"
        "វាយ `/set HH:MM សាររំលឹក` ឧទាហរណ៍៖\n"
        "`/set 07:00 ដល់ពេលត្រូវក្រោកពីគេងហើយ`\n"
        "`/set 11:00 ដល់ពេលត្រូវឈប់លេងទូរស័ព្ទហើយ`",
        parse_mode='Markdown'
    )

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args or len(context.args) < 1:
            await update.message.reply_text("❌ សូមបញ្ចូលម៉ោង! ឧទាហរណ៍៖ `/set 11:00 ដល់ពេលរៀន`", parse_mode='Markdown')
            return

        time_str = context.args[0]
        message = " ".join(context.args[1:]) if len(context.args) > 1 else "ដល់ពេលត្រូវធ្វើការងារហើយ!"

        # បំបែកម៉ោង និងនាទី
        time_parts = time_str.split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])

        # កំណត់ Timezone Cambodia
        cambodia_tz = pytz.timezone('Asia/Phnom_Penh')
        target_time = datetime.time(hour=hours, minute=minutes, tzinfo=cambodia_tz)

        # បន្ថែម Task ចូល Job Queue
        context.job_queue.run_daily(
            send_reminder,
            time=target_time,
            chat_id=update.effective_chat.id,
            data=message
        )

        await update.message.reply_text(f"✅ បានកំណត់ការរំលឹកនៅម៉ោង **{time_str}** រៀងរាល់ថ្ងៃ!\nសារ៖ {message}", parse_mode='Markdown')

    except Exception as e:
        # បង្ហាញ Error ពិតប្រាកដទៅ Telegram តែម្តង ដើម្បីងាយស្រួលដឹង
        await update.message.reply_text(f"❌ កើតមានបញ្ហា Error: `{str(e)}`", parse_mode='Markdown')

if __name__ == '__main__':
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