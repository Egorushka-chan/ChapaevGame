import hashlib
import os
import sqlite3
import pygame as pg, pygame_gui as pgui

STATIC_SALT = 'VintageStory'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
SOUND_FORCE = 0.1

pg.init()


def get_image(name: str):
    return os.path.join(DIR_PATH, 'Assets/Images/', name)


def get_music(name: str):
    return os.path.join(DIR_PATH, 'Assets/Music', name)


def get_font(name: str):
    return os.path.join(DIR_PATH, 'Assets/Fonts', name)


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
    def __init__(self, id: int, nickname: str, login: str, password: str):
        self.id: int = id
        self.nickname: str = nickname
        self.login: str = login
        self.password: str = password


class Database:
    def __init__(self):
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


class LoginScene:
    def __init__(self):
        resolution = 600, 900
        element_list = []
        ui_elements = []
        display = pg.display.set_mode(resolution)
        ui_manager = pgui.UIManager(resolution, 'Assets/theme.json')

        icon = pg.image.load(get_image('chapaev_title.png')).convert_alpha()
        pg.display.set_icon(icon)
        pg.display.set_caption('Компьютерная игра "Шашки-Чапаев"')

        scene_background = pg.image.load(get_image('login_form.png')).convert_alpha()
        element_list.append((scene_background, (0, 0)))

        # Добавляем новый шрифт вместо стандартного
        # samsung_font = pg.font.Font(get_font('SamsungSans-Regular.ttf'), 20)
        # ui_manager.add_font_paths(font_name='samsung',
        #                           regular_path=get_font('SamsungSans-Regular.ttf'),
        #                           bold_path=get_font('SamsungSans-Bold.ttf'))
        # ui_manager.preload_fonts([{'name': 'samsung', 'point_size': 14, 'style': 'regular'},
        #                           {'name': 'samsung', 'point_size': 18, 'style': 'regular'}])

        timer = pg.time.Clock()
        display.fill('White')

        main_label = pgui.elements.UILabel(relative_rect=pg.Rect(230, 160, 150, 70), manager=ui_manager,
                                           text='Авторизация',
                                           object_id="#mainlabel")
        login_label = pgui.elements.UILabel(relative_rect=pg.Rect(100, 210, 130, 70), manager=ui_manager, text='Логин (до 16)',
                                            object_id='#standart')
        login_textbox = pgui.elements.UITextEntryLine(relative_rect=pg.Rect(100, 260, 400, 50), manager=ui_manager)
        login_textbox.set_text_length_limit(16)

        # label = samsung_font.render('Авторизация', True, 'Black')
        # element_list.append((label, (230, 180)))
        loop = True
        time_delta = 0
        while loop:

            for element in element_list:
                display.blit(*element)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    loop = False
                ui_manager.process_events(event)

            ui_manager.update(time_delta)
            ui_manager.draw_ui(display)
            pg.display.flip()
            time_delta = timer.tick(100) / 1000


if __name__ == '__main__':
    LoginScene()
