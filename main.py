from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters, ApplicationBuilder
import logging
import dotenv
import os
from datetime import datetime, date, timedelta
import dbCRUD

dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, i'm Telegram Bot")


async def alarm(context: ContextTypes.DEFAULT_TYPE):
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Hey {job.data} seconds are over!")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cnx = dbCRUD.connect_to_db()
    if not cnx:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I could not connect to the database.")
        return
    user = update.effective_user
    tele_id = user.id
    f_name = user.first_name
    if not dbCRUD.check_member_exists(cnx, tele_id):
        dbCRUD.regist_member(cnx, f_name, tele_id, False)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello, {}! You are registered now".format(f_name)
        )
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Already registered!")
    cnx.close()


async def check_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today()
    chat_id = update.effective_chat.id
    tele_id = update.effective_user.id
    cnx = dbCRUD.connect_to_db()
    if not cnx:
        return await context.bot.send_message(chat_id=chat_id, text="I could not connect to the database.")
    if not dbCRUD.check_member_exists(cnx, tele_id):
        await context.bot.send_message(
            chat_id=chat_id,
            text="You need to register first.\n "
                 "/register to regist, then try again"
        )
        return
    exist_record = dbCRUD.check_record_set(cnx, tele_id, today, 'check_in')
    if exist_record:
        await context.bot.send_message(chat_id=chat_id, text=f"Check in is already recorded at {exist_record}")
        return
    if not dbCRUD.today_record_was_created(cnx, tele_id, today):
        await context.bot.send_message(
            chat_id=chat_id,
            text="Created record for %s" % today
        )
        dbCRUD.insert_record_time(cnx, tele_id, today)
    dbCRUD.update_record_time(
        cnx,
        tele_id,
        today,
        check_in=datetime.now().time().strftime("%H:%M:%S")
    )
    cnx.close()


async def remove_exist_job(chat_id: str, context: ContextTypes.DEFAULT_TYPE):
    """Remove job with Chat Id. Returns whether job was removed"""
    current_jobs = context.job_queue.get_jobs_by_name(chat_id)
    if current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can't go to the past!")
            return
        job_removed = remove_exist_job(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer set successfully!\n"
        if job_removed:
            text += f"Prev job :\n{job_removed}. Removed"
        await update.effective_message.reply_text(text)
    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set_timer")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a job if user change their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_exist_job(str(chat_id), context)
    text = "Timer canceled successfully!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


if __name__ == "__main__":
    bot = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    start_handler = CommandHandler('start', start)
    bot.add_handler(CommandHandler("set", set_timer))
    bot.add_handler(CommandHandler("unset", unset))
    bot.add_handler(CommandHandler("register", register))
    bot.add_handler(CommandHandler("check_in", check_in))
    bot.add_handler(start_handler)
    bot.run_polling(allowed_updates=Update.ALL_TYPES)
