import os
import random
import sys

import pygame as pg, pygame_gui as pgui
import re as regex

from Modules.BotPlayer import BotPlayer
from Modules.Database import Database, User
from Modules.Board import Board, Color

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def get_image(name: str):
    return os.path.join(DIR_PATH, 'Assets/Images/', name)


def get_music(name: str):
    return os.path.join(DIR_PATH, 'Assets/Music', name)


def get_font(name: str):
    return os.path.join(DIR_PATH, 'Assets/Fonts', name)


class AppContext:
    def __init__(self):
        self.database = Database(DIR_PATH)
        self.user = None
        self.current_scene = None

    def open_scene(self, scene):
        if scene == 'Login':
            self.current_scene = LoginScene(self, (600, 900))
        elif scene == 'Main':
            self.current_scene = MainScene(self, (1280, 720))
        else:
            ModuleNotFoundError(f'Сцены {scene} не существует')


class Scene:
    def __init__(self, appcontext: AppContext, resolution: (int, int)):
        pg.init()
        self.resolution = resolution
        self.ui_manager = pgui.UIManager(resolution, 'Assets/theme.json')
        self.display = pg.display.set_mode(resolution)
        self.display.fill('White')
        self.ui_elements = []
        self.pg_elements = []

        icon = pg.image.load(get_image('chapaev_title.png')).convert_alpha()
        pg.display.set_icon(icon)
        pg.display.set_caption('Компьютерная игра "Шашки-Чапаев"')

        self.timer = pg.time.Clock()

    def create_label(self, rectangle: (int, int, int, int), text, type):
        label = pgui.elements.UILabel(relative_rect=pg.Rect(*rectangle), manager=self.ui_manager,
                                      text=text,
                                      object_id=type)
        self.ui_elements.append(label)
        return label

    def create_button(self, rectangle: (int, int, int, int), text, type):
        button = pgui.elements.UIButton(relative_rect=pg.Rect(*rectangle), manager=self.ui_manager,
                                        text=text,
                                        object_id=type)
        self.ui_elements.append(button)
        return button

    def create_input(self, rectange: (int, int, int, int), hidden=False):
        textbox = pgui.elements.UITextEntryLine(relative_rect=pg.Rect(*rectange), manager=self.ui_manager)
        textbox.set_text_length_limit(16)
        textbox.set_text_hidden(hidden)
        self.ui_elements.append(textbox)
        return textbox

    def create_message(self, rectangle: (int, int, int, int), message: str):
        return pgui.windows.UIMessageWindow(pg.Rect(rectangle), message,
                                            self.ui_manager,
                                            window_title='Внимание', object_id='#message_window')

    def create_drop(self, rectangle: (int, int, int, int), list: list[str], start=1, type=None):
        start_value = list[start]
        if type is None:
            drop = pgui.elements.UIDropDownMenu(options_list=list, starting_option=start_value,
                                                relative_rect=pg.Rect(*rectangle), manager=self.ui_manager)
        else:
            drop = pgui.elements.UIDropDownMenu(options_list=list, starting_option=start_value,
                                                relative_rect=pg.Rect(*rectangle), manager=self.ui_manager,
                                                object_id=type)
        return drop


class MainScene(Scene):
    def __init__(self, appcontext: AppContext, resolution: (int, int)):
        self.hide_right = True
        if self.hide_right:
            resolution = 970, resolution[1]
        super().__init__(appcontext, resolution)

        self.battle_log = ''

        # создание разметки
        self.create_static_markup()

        hello_label = self.create_label((30, 24, 260, 31), 'Добро пожаловать!', '#mainlabel')
        nickname_label = self.create_label((30, 65, 260, 23), appcontext.user.nickname, '#standart')

        self.bot_button = self.create_button((27, 111, 256, 44), 'Новая игра с ботом', '#buttonblack')
        self.player_button = self.create_button((27, 186, 256, 44), 'Новая игра вдвоём', '#buttonblack')

        self.hide_music = True
        # музыкальная панель
        if not self.hide_music:
            music_main_panel = pgui.elements.UIPanel(pg.Rect(27, 263, 256, 233), manager=self.ui_manager,
                                                     object_id="#musicpanel")
            music_title_panel = pgui.elements.UIPanel(pg.Rect(56, 250, 93, 31), manager=self.ui_manager,
                                                      object_id="#musicpanel")
            music_title_label = self.create_label((63, 252, 75, 23), 'Музыка', '#musiclabel')

            self.music_drop = self.create_music_drop()

            music_loud_label = self.create_label((56, 342, 100, 55), 'Громкость', '#musiclabel')
            self.music_scroll = pgui.elements.UIHorizontalSlider(pg.Rect(56, 409, 196, 20), value_range=(0, 100),
                                                                     start_value=0,
                                                                     manager=self.ui_manager)

        if not self.hide_right:
            total_battles_label = self.create_label((59, 566, 102, 25), 'Кол-во игр', '#standart')
            self.total_bot_battles_label = self.create_label((56, 608, 104, 25),
                                                             f'С ботами: {appcontext.user.bot_games}',
                                                             '#standart')
            self.total_player_battles_label = self.create_label((56, 650, 90, 25),
                                                                f'Вдвоём: {appcontext.user.player_games}',
                                                                '#standart')

            match_info_label = self.create_label((1032, 24, 190, 25), 'Информация о матче', '#standart')
            self.match_player1_label = self.create_label((997, 74, 190, 25), 'Игрок 1:', '#standart')
            self.match_player2_label = self.create_label((997, 109, 190, 25), 'Игрок 2:', '#standart')
            match_log_textbox = pgui.elements.UITextBox('', pg.Rect(986, 150, 280, 214), manager=self.ui_manager,
                                                        object_id='#whitetextbox')

            control_main_label = self.create_label((1073, 393, 105, 22), 'Управление', '#standart')
            control = list()
            control.append('Задание слайдером')
            control.append('Интерактивное')
            self.control_drop = self.create_drop((998, 430, 260, 30), control)

            self.force_label = self.create_label((998, 508, 150, 25), f'Сила удара: {10.0}f', '#standart')
            self.force_scroll = pgui.elements.UIHorizontalSlider(pg.Rect(998, 545, 257, 20), value_range=(0.0, 10.0),
                                                                 start_value=10.0,
                                                                 manager=self.ui_manager)
        gs_r = (660, 720)

        self.game_surface = pg.Surface((660, 720))
        self.game_surface.fill('White')
        self.board_size = 550, 550
        self.indentations = ((gs_r[0] - self.board_size[0]) / 2), (gs_r[0] - self.board_size[1]) / 2
        self.pg_elements.append((self.game_surface, (310, 0)))
        self.board = Board(self.game_surface, self.board_size, self.indentations, DIR_PATH)

        self.loop = True
        self.time_delta = 0

        self.go_loop()

    def go_loop(self):
        while self.loop:
            for element in self.pg_elements:
                self.display.blit(*element)
            self.game_surface.fill('White')
            self.board.draw(self.time_delta)

            victory = self.board.check_victory()
            if victory:
                self.create_message((200, 200, 300, 200), victory)

            for event in pg.event.get():
                self.ui_manager.process_events(event)
                if event.type == pg.QUIT:
                    self.loop = False
                if event.type == pgui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.music_drop:
                        print("Music option:", event.text)
                    elif event.ui_element == self.control_drop:
                        print("Control option:", event.text)
                if event.type == pgui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.bot_button:
                        Board.start_new_game(self.board)
                        self.board.bot = BotPlayer(self.board.get_side_ids(Color.Black), self.board_size, (self.indentations[0], self.indentations[1]),
                                                   Color.Black)

                    elif event.ui_element == self.player_button:
                        Board.start_new_game(self.board)
                if event.type == pgui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == self.music_scroll:
                        print('Music slider:', event.value)
                    elif event.ui_element == self.force_scroll:
                        print('Force slider:', event.value)
                board_rect = self.game_surface.get_rect(topleft=(310, 0))
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if board_rect.collidepoint(event.pos):
                            self.board.process_click(
                                (event.pos[0] - 310, event.pos[1]))
                else:
                    try:
                        if pg.mouse.get_pressed()[0]:
                            if board_rect.collidepoint(event.pos):
                                self.board.process_handling(
                                    (event.pos[0] - 310, event.pos[1]), 1)
                    except:
                        pass

                if event.type == pg.MOUSEBUTTONDOWN and event.button == 3 and board_rect.collidepoint(event.pos):
                    self.board.forcing(True, (event.pos[0] - 310, event.pos[1]))
                elif event.type == pg.MOUSEBUTTONUP and event.button == 3 and self.board.force_choicer.visible:
                    self.board.forcing(False,
                                       (event.pos[0] - 310, event.pos[1]))

            self.ui_manager.update(self.time_delta)
            self.ui_manager.draw_ui(self.display)
            pg.display.flip()
            self.time_delta = self.timer.tick(100) / 1000

    def create_music_drop(self):
        path = os.path.join(DIR_PATH, 'Assets/Music')
        non_music = 'boom.mp3', 'turn_on.mp3'
        music = list()
        for files in os.listdir(path):
            if files[-4:] == '.mp3':
                if not files in non_music:
                    music.append(files)
        music_drop = self.create_drop((38, 290, 224, 30), music, type='#musicdrop')
        return music_drop

    def create_static_markup(self):
        grey_box1 = pg.Surface((310, 720))
        grey_box1.fill('#E3E3E3')
        self.pg_elements.append((grey_box1, (0, 0)))
        if not self.hide_right:
            grey_box2 = pg.Surface((310, 720))
            grey_box2.fill('#D9D9D9')
            self.pg_elements.append((grey_box2, (970, 0)))
            control_line = pg.Surface((280, 5))
            control_line.fill('black')
            self.pg_elements.append((control_line, (985, 380)))


class LoginScene(Scene):
    def __init__(self, appcontext: AppContext, resolution: (int, int)):
        super().__init__(appcontext, resolution)

        scene_background = pg.image.load(get_image('login_form.png')).convert_alpha()
        self.pg_elements.append((scene_background, (0, 0)))

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
        logined = False

        while loop:
            for element in self.pg_elements:
                self.display.blit(*element)

            for event in pg.event.get():
                self.ui_manager.process_events(event)
                if event.type == pg.QUIT:
                    loop = False
                if event.type == pgui.UI_BUTTON_PRESSED:
                    if event.ui_element == login_button:
                        if not login_error.visible and not password_error.visible:
                            result = appcontext.database.authorize_user(login_textbox.get_text(),
                                                                        password_textbox.get_text())
                            if result:
                                loop = False
                                logined = True
                                appcontext.user = User(*result[0])
                            else:
                                popup = self.create_message((200, 200, 300, 200), 'Пользователь не найден')

                    elif event.ui_element == registration_button:
                        if not login_error.visible and not password_error.visible and not nickname_error.visible:
                            try:
                                appcontext.database.registrate_user(nickname_textbox.get_text(),
                                                                    login_textbox.get_text(),
                                                                    password_textbox.get_text())
                            except BaseException as ex:
                                popup = self.create_message((200, 200, 300, 200), f'Ошибка {ex}')
                            else:
                                popup = self.create_message((200, 200, 300, 200), 'Пользователь зарегистрирован')
                                login_textbox.set_text('')
                                password_textbox.set_text('')
                                nickname_textbox.set_text('')
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
            self.ui_manager.draw_ui(self.display)
            pg.display.flip()
            time_delta = self.timer.tick(100) / 1000

        for element in self.ui_elements:
            element.kill()
        pg.quit()

        if logined:
            appcontext.open_scene('Main')

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


if __name__ == '__main__':
    app_context = AppContext()

    skip_authorisation = False
    for arg in sys.argv:
        if arg == '-skip':
            skip_authorisation = True

    if skip_authorisation:
        app_context.user = User(999, 'Anonymous', 'Anonymous', 'Anonymous')
        app_context.open_scene('Main')
    else:
        app_context.open_scene('Login')
