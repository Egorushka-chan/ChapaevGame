import hashlib
import os
import sqlite3

STATIC_SALT = 'VintageStory'


def generate_hash(password, login):
    # Вставляем посередине пароля логин
    salted_password = password[len(password) // 2:] + login + password[:len(password) // 2]
    # Убираем последний символ в пароле
    salted_password = salted_password[:-1]
    # Добавляем статическую соль
    salted_password.join(STATIC_SALT)

    # Создаём хеш пароля
    sha512_password = hashlib.sha512(salted_password.encode())
    # Возвращаем в шестнадцатеричном виде
    return sha512_password.hexdigest()


def close():
    pass


class User:
    def __init__(self, id: int, nickname: str, login: str, password: str, bot_games=0, player_games=0):
        self.id: int = id
        self.nickname: str = nickname
        self.login: str = login
        self.password: str = password
        self.bot_games = bot_games
        self.player_games = player_games


class Database:
    def __init__(self, DIR_PATH):
        self.db_path = os.path.join(DIR_PATH, 'database.db')
        if os.path.exists(self.db_path):
            self.conn = sqlite3.connect('database.db')
            self.cur = self.conn.cursor()
        else:
            # если файла базы данных не обнаружено, то создаём новую
            self.conn = sqlite3.connect('database.db')
            self.cur = self.conn.cursor()

            command = (r'CREATE TABLE "Users" ("ID"	INTEGER NOT NULL,"Nickname"	INTEGER NOT NULL,"Login"	INTEGER '
                       r'NOT NULL UNIQUE,"Password"	INTEGER NOT NULL,PRIMARY KEY("ID" AUTOINCREMENT))')
            self.cur.execute(command)
            command = ('CREATE TABLE "Games" ("ID"	INTEGER NOT NULL,"FirstPlayer"	INTEGER NOT NULL,"SecondPlayer"	'
                       'INTEGER NOT NULL,"Winner"	INTEGER NOT NULL,"GameTime"	INTEGER,"ReplayFile"	TEXT,'
                       'PRIMARY KEY("ID" AUTOINCREMENT),FOREIGN KEY("FirstPlayer") REFERENCES "Users"("ID"))')
            self.cur.execute(command)
            self.conn.commit()
        pass

    def query(self, command: str, values=None):
        if values:
            self.cur.execute(command, values)
        else:
            self.cur.execute(command)
        result = self.cur.fetchall()
        self.conn.commit()
        return result

    def authorize_user(self, login: str, password: str):
        password_hash = generate_hash(password, login)
        # поиск в базе данных
        values = (login, password_hash)
        res = self.query('SELECT * FROM Users WHERE Users.Login == ? and Users.Password == ?', (login, password_hash))
        return res

    def registrate_user(self, nick: str, login: str, password: str):
        password_hash = generate_hash(password, login)
        # запись в базу данных
        values = (nick, login, password_hash)
        self.query('INSERT INTO Users(Nickname, Login, Password) Values (?,?,?)', values)
