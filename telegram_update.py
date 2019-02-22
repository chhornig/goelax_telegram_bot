import dbhandler
import json
from datetime import date, datetime


def introduction(user):
    response = "Hallo, dies ist der Trainingsbot. \nHier kannst Du dich fuer das Training an- und abmelden. \nUm zu starten, gib bitte deinen Namen ein."
    dbhandler.set_thread(user, "start")
    dbhandler.add_user(user)
    return response

def thread_start(user, text):
    name = dbhandler.add_name(text, user)
    response = 'Danke! Du bist jetzt unter dem Namen "{}" bekannt.'.format(name)
    dbhandler.set_thread(user, "position")
    positions = ["Goalie","Close Defense", "Long Stick Middie","Middie", "Attack"]
    keyboard = build_keyboard(positions)
    return keyboard, response

def thread_position(user, text):
    position = text
    dbhandler.add_position(position, user)
    response = 'Deine Position wurde auf "{}" geaendert.'.format(position)
    dbhandler.set_thread(user, None)
    return response

def thread_absage(user, text):
    if text.startswith("Dauerhaft"):
        response = "Schade, dass Du nicht mehr zum Training kommen kannst. Melde dich bald wieder an!"
        dbhandler.set_active(user, False)
    else:
        db_text = datetime.strptime(text, "%A, %d.%m.%y %H:%M")
        if dbhandler.new_absage(db_text, user):
            response = 'Du wurdest erfolgreich fuer das Training "{}" abgemeldet.'.format(text)
    dbhandler.set_thread(user, None)
    return response

def get_absagen(user):
    absagen = dbhandler.get_absagen_user(user)
    absagen = dbhandler.dbdate_to_string(absagen)
    if absagen:
        response = absagen
    else:
        response = "Du bist für alle kommenden Trainings abgemeldet."
    return response

def next(user):
    trainings = dbhandler.next_trainings()
    trainings = dbhandler.dbdate_to_string(trainings)
    return trainings

def activate(user):
    dbhandler.set_active(user, True)
    response = "Du bist jetzt wieder für alle Trainings angemeldet. Die nächsten Trainings sind:\n"
    trainings = dbhandler.next_trainings()
    for i in trainings:
        response+=i
        response+="\n"
    return response

def absage(user):
    liste_training = []
    liste_training = dbhandler.next_trainings()
    liste_training.append("Dauerhaft")
    keyboard = build_keyboard(liste_training)
    response = "Waehle das Training, fuer das Du dich abmelden moechtest:"
    dbhandler.set_thread(user, "absage")
    return keyboard, response

def new_training(user):
    if dbhandler.is_admin(user):
        dbhandler.set_thread(user, "training")
        response = "Gib das Datum des Trainings ein."
    else:
        response = "Forbidden"
    return response

def training(user, text):
    if dbhandler.new_training(text):
        response = "Erfolg!"
    else:
        response = "fail!"
    dbhandler.set_thread(user, None)
    return response

def next_trainings():
    response = str()
    for i in dbhandler.next_trainings():
        response = response + i + "\n"
    return response

def name(user, text):
    name_text = "Du bist jetzt bekannt als{}".format(text[5:])
    dbhandler.add_to_db(text[5:], "name", "players", "T_id", user)
    send_message(name_text, chat)
    return response


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)
