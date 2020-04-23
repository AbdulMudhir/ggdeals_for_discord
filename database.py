import sqlite3


class DataBase(sqlite3.Connection):

    def __init__(self, dataBasePath):
        sqlite3.Connection.__init__(self, dataBasePath)
        self.cursor = self.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE wish(
                                username TEXT ,
                                user_id INTEGER ,
                                game_name TEXT,
                                notified INTEGER
                                
                                
                                
                                )''')

        self.commit()

    def create_game_table(self):
        self.cursor.execute('''CREATE TABLE game(
        
                                game_title TEXT UNIQUE,
                                game_price TEXT,
                                game_image TEXT,
                                direct_link TEXT,
                                historical TEXT,
                                genre TEXT,
                                video_link TEXT   



                                )''')

        self.commit()

    def add_wish_list(self, user, game_name):
        game_to_add = {'username': user.name,
                       'user_id': user.id,
                       'game_name': game_name,
                       'notified': 0
                       }

        self.cursor.execute('''INSERT OR IGNORE INTO wish( username, user_id, game_name, notified) 
        VALUES (:username, :user_id, :game_name, :notified)''', game_to_add)

        self.commit()

    def view_user_wish_list(self, user):
        self.cursor.execute('''SELECT game_name FROM wish WHERE user_id =:user_id''', {'user_id': user.id})
        return self.cursor.fetchall()

    def game_exist(self, user, game_title):
        self.cursor.execute('''SELECT game_name FROM wish WHERE user_id =:user_id AND game_name = :game_name''',
                            {'user_id': user.id,
                             'game_name': game_title})
        return self.cursor.fetchone() is not None

    def remove_wish_list(self, user, game_name):
        self.cursor.execute('''DELETE FROM wish WHERE user_id = :user_id AND game_name =:game_name ''',
                            {'user_id': user.id, 'game_name': game_name})

        self.commit()

    def view_wish_list(self):
        self.cursor.execute('SELECT DISTINCT game_name FROM wish ')
        return self.cursor.fetchall()

    def get_game(self, game_name):
        self.cursor.execute('SELECT game_title FROM game WHERE game_title =:game_name ', {'game_name' : game_name})
        return self.cursor.fetchone()

    def add_game(self, kwarg):
        self.cursor.execute('''INSERT OR IGNORE INTO game(game_title,game_price, game_image, direct_link, historical,
        genre, video_link) VALUES (:game_name, :game_price, :game_picture, :direct_link, :historical, :genre, :video_link)''', kwarg)

        self.commit()


    def get_user_with_game_list(self, game_title):
        self.cursor.execute('''SELECT user_id FROM wish WHERE game_name =:game_name and notified =0''', {'game_name': game_title})
        return self.cursor.fetchall()

    def set_user_notified_for_game(self, user, game_title):
        self.cursor.execute('''UPDATE wish SET notified = 1 WHERE user_id =:user_id AND game_name = :game_name''',{'user_id': user.id,'game_name': game_title})
        self.commit()