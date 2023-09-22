import telebot
import os
from pos_system.celery import app


@app.task(name="send_db_backup_to_telegramusers_task")
def send_db_backup_to_telegramusers_task():
    directory_path = '/var/db_dumps/'
    print("Directory Path: ", directory_path)
    for entry in os.scandir(directory_path):
        if entry.is_file():
            try:
                most_recent_file = entry.name
                if not most_recent_file.endswith(".gz"):
                    continue
                print("File Name: ", entry.name)
                bot = telebot.TeleBot('6663339888:AAGACkXkrUmjm3xq2rWtVUJ4lgPa2CXBo1A')
                chat_id = '-4046728742'
                with open(directory_path + most_recent_file, 'rb') as dump:
                    bot.send_document(chat_id, dump)
                
                # Delete the zipped dump file
                os.remove(directory_path + most_recent_file)
            except Exception as e:
                # Handle any errors here
                print("Error", directory_path + most_recent_file, e)
    