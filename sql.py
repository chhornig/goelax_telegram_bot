'''
Created on 23.11.2018

@author: hornig2
'''
import sqlalchemy
import pandas as pd
import random, string
from pandas.io import sql
from mytelegram import *


telegram_commands = ["zusagen_anzeigen('20180515')"]

if __name__ == '__main__':
    main()

engine = sqlalchemy.create_engine('mysql+pymysql://root:telegrambot@localhost:3306/telegram')

query = "UPDATE `telegram`.`players` SET `position` = '3' WHERE (`player_id` = '39');"

engine.execute()

class player():
    def __init__(self):
        print("Wilkommen beim GoeLax Trainingsbot! Wie heisst Du?")
        self.name = input()
        new_player = pd.DataFrame({'name' : [self.name]})
        new_player.to_sql(
            name = 'players',
            con = engine,
            index = False,
            if_exists='append')
        print("Hi, {}".format(self.name))
            
    def add_position(self):
        print(new_player)
        
    
    def add_name(self, name):
        self.name = name
        
    def add_telegram_id(self, T_id):
        self.T_id = T_id        
        
    
    
#peter = player()
#peter.add_position()
    
        
    
    
    

def new_training (date):
    new_training = pd.DataFrame({'date' : [date]})
    new_training.to_sql(
        name = 'trainings',
        con = engine,
        index = False,
        if_exists='append')

def new_absage (date, player_id):
    absagezeitpunkt = datetime.datetime.now()
    new_absage = pd.DataFrame({'player_id' : [player_id],
                               'date' : date,
                               'absagezeitpunkt' : absagezeitpunkt})
    new_absage.to_sql(
        name = 'absagen',
        con = engine,
        index = False,
        if_exists='append')

# Gibt die Absagen fuer das Trainings zurueck. Wenn keine Absagen vorhanden sind, gibt es "keine Absagen" zurueck, wenn kein Training stattfindet "kein Training"
def absagen_anzeigen (date): 
    t_query = ("select trainings.date from trainings where trainings.date = '" + date + "'")
    trainings = pd.read_sql_query(t_query, engine)
    if not trainings.empty:
        query = ("select players.name, absagen.date, absagen.absagezeitpunkt from telegram.players inner join absagen on players.player_id = absagen.player_id where absagen.date = '" + date + "';")
        absagen = pd.read_sql_query(query, engine)
        if absagen.empty:
            return "keine Absagen"
        return absagen
    else:
        return "kein Training"
  

def zusagen_anzeigen (date): 
    t_query = ("select trainings.date from trainings where trainings.date = '" + date + "'")
    trainings = pd.read_sql_query(t_query, engine)
    if not trainings.empty:
        query = ("select * from telegram.players where players.player_id not in (select absagen.player_id from absagen where absagen.date = '" + date + "');")
        zusagen = pd.read_sql_query(query, engine)
        print(zusagen)
        if zusagen.empty:
            return "keine Absagen"
        return zusagen
    else:
        return "kein Training"

positionen_deutsch = {0 : 'Goalie',
                          1:'Longstick',
                          2:'LSM',
                          3:'Middie',
                          4:'Attack'}
# Gibt Uebersicht ueber alle Positionen entsprechend dem Woerterbuch zurueck
def uebersicht_positionen(woerterbuch_positionen):
    query = ("SELECT position, count(*) FROM telegram.players GROUP BY position")
    positionen = pd.read_sql_query(query, engine)
    positionen = positionen.rename(columns={"count(*)": "count"})
    for i in range(len(positionen)):
        poscount = positionen[positionen['position'] == i]['count']
        print(woerterbuch_positionen[i] + ': ' + str(int(poscount)))
#uebersicht_positionen(positionen_deutsch) 




'''
testliste = ["a", "wert", "wertung"]
teststring = "a"
if teststring in testliste:
    print("YO")
else:
    print("NO")
'''
