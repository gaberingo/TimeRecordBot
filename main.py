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


def check_database(tele_id, command=None):
    today = date.today()
    cnx = dbCRUD.connect_to_db()
    if not cnx:
        return False, "I could not connect to the database."
    if not dbCRUD.check_member_exists(cnx, tele_id):
        return False, "You need to register first.\n /register to regist, then try again"
    if command is not None:
        exist_record = dbCRUD.check_record_set(cnx, tele_id, today, command)
        if exist_record:
            return False, f"{command} is already recorded"
    if not dbCRUD.today_record_was_created(cnx, tele_id, today):
        dbCRUD.insert_record_time(cnx, tele_id, today)
        return cnx, "Created record for %(today)s" % {"today": today}

    return cnx, None


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
    chat_id = update.effective_chat.id
    tele_id = update.effective_user.id
    cnx, msg = check_database(tele_id, "check_in")
    if cnx:
        time = datetime.now().time().strftime("%H:%M:%S")
        await context.bot.send_message(chat_id=chat_id, text=f"Checking in: {time}")
        dbCRUD.update_record_time(
            cnx,
            tele_id,
            date.today(),
            check_in=time
        )
        cnx.close()
        return
    else:
        await context.bot.send_message(chat_id=chat_id, text=msg)
        return

async def break_out1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tele_id = update.effective_user.id
    cnx, msg = check_database(tele_id, "break_out1")
    if cnx:
        time = datetime.now().time().strftime("%H:%M:%S")
        await context.bot.send_message(chat_id=chat_id, text=f"Breaking out 1: {time}")
        dbCRUD.update_record_time(
            cnx,
            tele_id,
            date.today(),
            break_out1=time
        )
        cnx.close()
    else:
        await context.bot.send_message(chat_id=chat_id, text=msg)


async def break_in1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tele_id = update.effective_user.id
    cnx, msg = check_database(tele_id, "break_in1")
    if cnx:
        time = datetime.now().time().strftime("%H:%M:%S")
        await context.bot.send_message(chat_id=chat_id, text=f"Breaking In 1: {time}")
        dbCRUD.update_record_time(
            cnx,
            tele_id,
            date.today(),
            break_in1=time
        )
        cnx.close()
    else:
        await context.bot.send_message(chat_id=chat_id, text=msg)


async def break_out2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tele_id = update.effective_user.id
    cnx, msg = check_database(tele_id, "break_out2")
    if cnx:
        time = datetime.now().time().strftime("%H:%M:%S")
        await context.bot.send_message(chat_id=chat_id, text=f"Breaking out 2: {time}")
        dbCRUD.update_record_time(
            cnx,
            tele_id,
            date.today(),
            break_out2=time
        )
        cnx.close()
    else:
        await context.bot.send_message(chat_id=chat_id, text=msg)


async def break_in2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tele_id = update.effective_user.id
    cnx, msg = check_database(tele_id, "break_in2")
    if cnx:
        time = datetime.now().time().strftime("%H:%M:%S")
        await context.bot.send_message(chat_id=chat_id, text=f"Breaking In 2: {time}")
        dbCRUD.update_record_time(
            cnx,
            tele_id,
            date.today(),
            break_in2=time
        )
        cnx.close()
    else:
        await context.bot.send_message(chat_id=chat_id, text=msg)


async def check_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tele_id = update.effective_user.id
    cnx, msg = check_database(tele_id, "check_out")
    if cnx:
        time = datetime.now().time().strftime("%H:%M:%S")
        await context.bot.send_message(chat_id=chat_id, text=f"Check out: {time}")
        dbCRUD.update_record_time(
            cnx,
            tele_id,
            date.today(),
            check_out=time
        )
        cnx.close()
    else:
        await context.bot.send_message(chat_id=chat_id, text=msg)


async def show_data_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tele_id = update.effective_user.id
    cnx, msg = check_database(tele_id)
    if cnx:
        data_today = dbCRUD.show_data_today(cnx, tele_id, date.today())
        text_msg = ""
        labels = ["Hari ini", "Check In", "Break Out1", "Break In1", "Break Out2", "Break In2", "Check Out"]
        # Membuat perulangan untuk setiap elemen data dan label
        for label, item in zip(labels, data_today):
            if type(item) == datetime.date:
                formatted_item = item.strftime("%d %B %Y")
            elif type(item) == timedelta:
                formatted_item = str(item)
            else:
                formatted_item = str(item)
            text_msg += (f"{label}: {formatted_item}\n")
        await context.bot.send_message(chat_id=chat_id, text=text_msg)
    else:
        await context.bot.send_message(chat_id=chat_id, text=msg)
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
    bot.add_handler(CommandHandler("break_out1", break_out1))
    bot.add_handler(CommandHandler("break_in1", break_in1))
    bot.add_handler(CommandHandler("break_out2", break_out2))
    bot.add_handler(CommandHandler("break_in2", break_in2))
    bot.add_handler(CommandHandler("check_out", check_out))
    bot.add_handler(CommandHandler("show_today", show_data_today))
    bot.add_handler(start_handler)
    bot.run_polling(allowed_updates=Update.ALL_TYPES)
