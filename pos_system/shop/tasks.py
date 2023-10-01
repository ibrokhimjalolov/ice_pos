import telebot
import os
from pos_system.celery import app
from .utils import Bot, CHAT_ID


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
                with open(directory_path + most_recent_file, 'rb') as dump:
                    Bot.send_document(CHAT_ID, dump)
                # Delete the zipped dump file
                os.remove(directory_path + most_recent_file)
            except Exception as e:
                # Handle any errors here
                print("Error", directory_path + most_recent_file, e)
