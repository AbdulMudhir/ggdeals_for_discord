import sqlite3



class DataBase(sqlite3.Connection):

    def __init__(self, dataBasePath):
        sqlite3.Connection.__init__(self, dataBasePath)
        self.cursor = self.cursor()


    def create_table(self):
        self.cursor.execute('''CREATE TABLE wish(
                                username TEXT ,
                                user_id INTEGER UNIQUE,
                                game_name TEXT UNIQUE,
                                notified INTEGER
                                
                                
                                
                                )''')

        self.commit()


    def add_wish_list(self, user, game_name):

        game_to_add = {'username':user.name,
                       'user_id': user.id,
                       'game_name':game_name,
                       'notified': 0
        }

        self.cursor.execute('''INSERT OR IGNORE INTO wish( username, user_id, game_name, notified) 
        VALUES (:username, :user_id, :game_name,:notified)''', game_to_add)