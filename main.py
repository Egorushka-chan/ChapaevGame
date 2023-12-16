import hashlib
import os
import sqlite3
import pygame as pg, pygame_gui as pgui
import re as regex

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


class AppContext:
    def __init__(self):
        self.database = Database()
        self.user = None


class LoginScene:
    def __init__(self, appcontext : AppContext):
        resolution = 600, 900
        self.element_list = []
        self.ui_elements = []
        display = pg.display.set_mode(resolution)

        # Очень важная строка. Стили, хранятся в папке Assets
        self.ui_manager = pgui.UIManager(resolution, 'Assets/theme.json')

        icon = pg.image.load(get_image('chapaev_title.png')).convert_alpha()
        pg.display.set_icon(icon)
        pg.display.set_caption('Компьютерная игра "Шашки-Чапаев"')

        scene_background = pg.image.load(get_image('login_form.png')).convert_alpha()
        self.element_list.append((scene_background, (0, 0)))

        timer = pg.time.Clock()
        display.fill('White')

        # создание разметки
        main_label = self.create_label((230, 160, 150, 70), 'Авторизация', "#mainlabel")
        login_label = self.create_label((100, 210, 130, 70), 'Логин (6-16)', '#standart')
        login_textbox = self.create_input((100, 260, 400, 50))
        password_label = self.create_label((100, 310, 130, 50), 'Пароль (6-16)', '#standart')
        password_textbox = self.create_input((100, 360, 400, 50), True)
        login_button = self.create_button((200, 430, 200, 50), 'Войти', "#buttongreen")
        registration_label = self.create_label((230, 480, 150, 70), 'Регистрация', "#mainlabel")
        info_label = self.create_label((100, 530, 300, 50), 'Заполните верхние поля, а также:', '#standart')
        nickname_label = self.create_label((100, 570, 150, 50), 'Никнейм (6-16)', "#standart")
        nickname_textbox = self.create_input((100, 620, 400, 50))
        registration_button = self.create_button((200, 700, 200, 50), 'Создать аккаунт', "#buttonred")

        # ошибки
        login_error = self.create_label((250, 210, 200, 70), 'Неправильный логин', "#errorlabel")
        password_error = self.create_label((250, 310, 200, 50), 'Неправильный пароль', "#errorlabel")
        nickname_error = self.create_label((250, 570, 200, 50), 'Неправильный ник', "#errorlabel")

        loop = True
        time_delta = 0

        while loop:
            for element in self.element_list:
                display.blit(*element)

            for event in pg.event.get():
                self.ui_manager.process_events(event)
                if event.type == pg.QUIT:
                    loop = False
                if event.type == pgui.UI_BUTTON_PRESSED:
                    if event.ui_element == login_button:
                        if not login_error.visible and not password_error.visible:
                            result = appcontext.database.authorize_user(login_textbox.get_text(), password_textbox.get_text())
                            if result:
                                loop = False
                                appcontext.user = User(*result)
                            else:
                                popup = pgui.windows.UIMessageWindow(pg.Rect(200, 200, 200, 200),
                                                                     'Пользователь не найден',
                                                                     self.ui_manager,
                                                                     window_title='D', object_id='#message_window')

                    elif event.ui_element == registration_button:
                        if not login_error.visible and not password_error.visible and not nickname_error.visible:
                            print('Registration button pressed')
                if event.type == pgui.UI_TEXT_ENTRY_CHANGED:
                    if event.ui_element == login_textbox:
                        validation = self.validation(login_textbox.get_text(), specials=True)
                        if validation:
                            login_error.visible = 1
                            login_error.set_text(validation)
                        else:
                            login_error.visible = 0
                    if event.ui_element == password_textbox:
                        validation = self.validation(password_textbox.get_text())
                        if validation:
                            password_error.visible = 1
                            password_error.set_text(validation)
                        else:
                            password_error.visible = 0
                    if event.ui_element == nickname_textbox:
                        validation = self.validation(nickname_textbox.get_text(), specials=True)
                        if validation:
                            nickname_error.visible = 1
                            nickname_error.set_text(validation)
                        else:
                            nickname_error.visible = 0

            self.ui_manager.update(time_delta)
            self.ui_manager.draw_ui(display)
            pg.display.flip()
            time_delta = timer.tick(100) / 1000

    def create_label(self, rectangle, text, type):
        label = pgui.elements.UILabel(relative_rect=pg.Rect(*rectangle), manager=self.ui_manager,
                                      text=text,
                                      object_id=type)
        self.ui_elements.append(label)
        return label

    def create_button(self, rectangle, text, type):
        button = pgui.elements.UIButton(relative_rect=pg.Rect(*rectangle), manager=self.ui_manager,
                                        text=text,
                                        object_id=type)
        self.ui_elements.append(button)
        return button

    def create_input(self, rectange, hidden=False):
        textbox = pgui.elements.UITextEntryLine(relative_rect=pg.Rect(*rectange), manager=self.ui_manager)
        textbox.set_text_length_limit(16)
        textbox.set_text_hidden(hidden)
        self.ui_elements.append(textbox)
        return textbox

    def validation(self, text, specials=False):
        result = ''
        if len(text) < 6:
            result += 'Длина;'
        for char in text:
            if char.isspace():
                result += 'Пробел;'
        if specials:
            # убираем все кроме совместимых символов
            symbols = regex.findall(r'([^0-9|^a-zA-Z])+', text)
            if symbols:
                result += 'Спец. символы'
        return result


# class Popup:
#     def __init__(self, parent_surface, message):
#         self.parent_surface = parent_surface
#         self.message = message
#         self.surface = pg.Surface((0, 0))
#         self.surface.fill('White')
#         self.showing_progress = 0
#         self.speed = 1000  # сколько миллисекунд развёртывание
#
#         self.font = pg.Font(get_font('SamsungSans-Regular.ttf'), size=44)
#         self.render = self.font.render(message, True, 'Black').convert_alpha()
#         self.resolution = self.render.get_width() + 20, self.render.get_height() + 20
#         self.ui_manager = pgui.UIManager(self.resolution)
#         self.button = pgui.elements.UIButton(relative_rect=pg.Rect(50,50,50,50), manager=self.ui_manager,
#                                         text='OK')
#
#     def draw(self, time_delta):
#         if self.showing_progress < 1:
#             self.showing_progress = self.showing_progress + (1000 / self.speed) * time_delta
#
#             current_x = self.resolution[0] * self.showing_progress
#             current_y = self.resolution[1] * self.showing_progress
#
#             self.surface = pg.Surface((current_x, current_y))
#             self.surface.fill('White')
#             self.button.set_dimensions((current_x,current_y))
#
#
#             self.surface.blit(pg.transform.smoothscale(self.render, (current_x, current_y)), (0, 0))
#             self.parent_surface.blit(self.surface, (20, 20))
#             self.ui_manager.update(time_delta)
#             self.ui_manager.draw_ui(self.parent_surface)
#
#             print(f'{self.showing_progress:.2}')
#         else:
#             pass


if __name__ == '__main__':
    LoginScene(AppContext())
