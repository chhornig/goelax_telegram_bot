'''
Created on 28.11.2018

@author: hornig2
'''


import datetime
import json
import requests
import time
import urllib
import dbhandler
import telegram_update
import sqlalchemy
from datetime import date, datetime
from sqlalchemy.testing.config import db_opts
from dbhandler import set_thread

TOKEN = "772144543:AAHV6QROGyghfB9L6RtAbtclLwDeGyNgUcA"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

db = dbhandler.engine


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            user = update["message"]["from"]["id"]
            response = "Ich verstehe nicht."
            keyboard = None
            thread = dbhandler.get_thread(user)
            if text == "/start":
                response = telegram_update.introduction(user)
            elif text == "/get_absagen":
                response = telegram_update.get_absagen(user)
            elif text == "/next":
                response = telegram_update.next(user)
            elif text == "/activate":
                response = telegram_update.activate(user)
            elif thread == None:
                if text.startswith("/absage"):
                    keyboard, response = telegram_update.absage(user)
                elif text.startswith("/next_trainings"):
                    response = telegram_update.next_trainings(user)
                elif text.startswith("/new_training"):
                    response = telegram_update.new_training(user)
                elif text.startswith("/name"):
                    response = telegram_update.name()
            elif thread == "training":
                response = telegram_update.training(user, text)
            elif thread == "start":
                keyboard, response = telegram_update.thread_start(user, text)
            elif thread == "position":
                response = telegram_update.thread_position(user, text)
            elif thread == "absage":
                response = telegram_update.thread_absage(user, text)
            send_message(response, chat, keyboard)
        except KeyError:
            pass

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)



if __name__ == '__main__':
    main()
