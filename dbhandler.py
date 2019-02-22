'''
Created on 29.11.2018

@author: hornig2
'''

import sqlalchemy
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DATE, DATETIME
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import func
from datetime import date, datetime
import re


Integer = mysql.INTEGER

global engine
engine = sqlalchemy.create_engine('mysql+pymysql://root:01AovcMVD2wVkzvnMIWl@localhost:3306/telegram')

Session = sessionmaker(bind=engine)

Base = declarative_base()


class Player(Base):
    __tablename__= 'players'
    player_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    position = Column(Integer(32))
    active = Column(Boolean, default=True)
    Telegram_user = Column(String(50))
    Admin = Column(Boolean, default=False)

class Thread(Base):
    __tablename__='Thread'
    thread_id = Column(Integer, primary_key=True, autoincrement=True)
    thread = Column(String(50))
    Telegram_user = Column(Integer(32), unique=True)

class Training(Base):
    __tablename__='trainings'
    training_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DATETIME(timezone=True), unique=True)

class Absagen(Base):
    __tablename__='absagen'
    absage_id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer)
    training_id  = Column(Integer)
    absagezeitpunkt = Column(DATETIME(timezone=True), server_default=func.now())

def user_exists(T_id):
    session = Session()
    if session.query(Player).filter(Player.Telegram_user == T_id).first():
        return True
    else:
        return False

def new_training(training_date):
    new_training = Training(date=training_date)
    session = Session()
    for training in session.query(Training).\
        filter(Training.date == new_training.date):
        return False
    session.add(new_training)
    session.commit()
    return True

def add_user(T_id):
    session = Session()
    #new_user = session.query(Player).filter(Player.Telegram_user == T_id).first()
    #new_user == None
    new_user = Player(Telegram_user = T_id)
    session.add(new_user)
    new_thread = Thread(Telegram_user = T_id)
    session.add(new_thread)
    session.commit()

def add_name(name, T_id):
    session = Session()
    new_player = session.query(Player).filter(Player.Telegram_user == T_id).first()
    new_player.name = name
    session.commit()
    return new_player.name

def add_position(position, T_id):
    session = Session()
    new_player = session.query(Player).filter(Player.Telegram_user == T_id).first()
    positionsdict = {"Goalie": 1, "Close Defense":2,"Long Stick Middie":3,"Middie":4, "Attack":5}
    new_player.position = positionsdict[position]
    session.commit()
    return new_player.position

def set_thread(T_id, state):
    session = Session()
    setthread = session.query(Thread).filter(Thread.Telegram_user == T_id).first()
    setthread.thread = state
    session.commit()
    return setthread.thread

def get_thread(T_id):
    session = Session()
    setthread = session.query(Thread).filter(Thread.Telegram_user == T_id).first()
    session.commit()
    return setthread.thread

def is_admin(T_id):
    session = Session()
    if session.query(Player.Admin).filter(Player.Telegram_user == T_id):
        return True
    else:
        return False

def next_trainings():
    session = Session()
    trainings = session.query(Training.date).filter(Training.date > datetime.now()).order_by(Training.date).limit(6).all()
    return trainings

def new_absage(absage_date, T_id):
    neue_absage = Absagen()                                             #Klasse Absage erzeugen
    session = Session()                                                 #SQL-Session starten
    training_date = session.query(Training.training_id).\
        filter(Training.date == absage_date).first()                    #in Tabelle "training" (s. Klasse "Trainings") Trainings-ID ahnahd von an Funktion uebergebenem Datum ermitteln und in Variable speichern.
    if training_date == None:
        session.rollback()                                              #pruefen, ob Abfrage erfolgreich war, wenn nicht, Session beenden, weil kein Trianing an diesem Datum stattfindet
        return "kein Training"
    else:                                                               #in Tabelle "players" (s. Klasse "Player") Player-ID ahnahd von an Funktion uebergebener Telegram_ID ermitteln und in Variable speichern.
        player_id = session.query(Player.player_id).\
        filter(Player.Telegram_user == T_id).first()
    if player_id == None:
        session.rollback()                                              #pruefen, ob Abfrage erfolgreich war, wenn nicht, Session beenden, weil kein Spieler mit dieser Telegram_ID angemeldet ist
        return "kein Spieler"
    player_id = str(player_id)                                          #ermittelte Spieler_ID und Trainings_ID in String, und dann in reine Zahl umwandeln, dann in Klasse speichern
    neue_absage.player_id = int(re.search(r'\d+', player_id).group())
    training_date = str(training_date)
    neue_absage.training_id = int(re.search(r'\d+', training_date).group())
    doppelcheck = session.query(Absagen.player_id).\
        filter(Absagen.player_id == neue_absage.player_id).\
        filter(Absagen.training_id == neue_absage.training_id).first()  #pruefen, ob Spieler schon fuer dieses Training abgemeldet ist
    if doppelcheck != None:
        session.rollback()
        return "Spieler schon fuer dieses Training abgemeldet."
    session.add(neue_absage)
    session.commit()
    return True

def set_active(T_id, state): #setzt den Boolean-Wert auf die in 'state' übergebenen Wert und gibt den neuen Wert zur Kontrolle zurück
    session = Session()                                                 #SQL-Session starten
    player = session.query(Player).filter(Player.Telegram_user == T_id).first()
    if player.active != state:
        player.active = state
        session.commit()
    else:
        session.rollback()
    return player.active

def check_activity(T_id):
    session = Session()
    check = session.query(Player.active).filter(Player.Telegram_user).first()
    for i in check:
        checkbool = i
    return checkbool

def get_absagen_user(T_id): #gibt tuple der daten zurück
    session = Session()
    if check_activity(T_id):
        player = session.query(Player.player_id).filter(Player.Telegram_user == T_id)
        absagen_id = session.query(Absagen.training_id).filter(Absagen.player_id.in_(player))
        absagen_date = session.query(Training.date).filter(Training.training_id.in_(absagen_id)).all()
        return absagen_date
    else:
        return False

def dbdate_to_string(dbtimes): #nimmt tuple von Zeiteinheiten aus der Datenbank und überführt sie in einen String zur Ausgabe im Bot
    list = ''
    for i in dbtimes:
        list+=date.strftime(i.date, "%A, %d.%m.%y %H:%M")
        list+="\n"
    return list

def zusagen_anzeigen(date):
    session = Session()
    subsubquery = session.query(Training.training_id).filter(Training.date == date)
    subquery = session.query(Absagen.player_id).filter(Absagen.training_id.in_(subsubquery))
    query = session.query(Player.name)
    #gibt Liste an Strings zurueck
    teilnehmer = []
    for player in query.filter(Player.player_id.notin_(subquery)).all():
        testplayer = Player()
        testplayer.name = player.name
        teilnehmer.append(player.name)
    return teilnehmer
    #alternativ Rueckgabe von Liste von Tuples
    #teilnehmer = query.filter(Player.player_id.notin_(subquery)).all()
    #return (teilnehmer)

Base.metadata.create_all(engine)
