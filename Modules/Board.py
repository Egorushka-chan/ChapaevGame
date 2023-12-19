import os
import math
from enum import Enum

import pygame as pg


def calculate_point_diffs(point1, point2):
    """ Тригонометрическая работа с точками

    :param point1: точка №1
    :param point2: точка №2
    """
    # разница между точками
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    # dy впереди из-за позиционирования pygame. -dx что-бы 1 четверть была начальной.
    # Углы растут с 1 (от 0) до 4 степени (до 360)
    rads = math.atan2(dy, -dx)
    rads %= 2 * math.pi
    degs = math.degrees(rads)
    # x и y нужны для расчета направления шашки
    x = math.cos(rads)
    y = math.sin(rads)
    return degs, rads, x, y


class Checker:
    class Color(Enum):
        Black = 0
        White = 1

    def __init__(self, parent_surface, center: (int | float, int | float), mass, diameter, side: Color, dir_path):
        self.dir_path = dir_path
        self.center = center
        self.diameter = diameter
        self.mass = mass
        self.parent_surface = parent_surface
        self.side = side

        # выбор шашки и её свечение при этом
        self.selected: bool = False
        self.shine = pg.image.load(os.path.join(self.dir_path, 'Assets/Images/shine.png')).convert_alpha()
        self.shine_range = 10
        self.shine = pg.transform.scale(self.shine, (
            (self.diameter + self.shine_range) * 2, (self.diameter + self.shine_range) * 2))

        # цвет обводки и спрайт шашки
        self.color = ''
        if self.side == self.Color.White:
            self.color = "White"
            image_path = os.path.join(self.dir_path, 'Assets/Images/white_checker.png')
        else:
            self.color = "Black"
            image_path = os.path.join(self.dir_path, 'Assets/Images/black_checker.png ')
        self.image = pg.image.load(image_path).convert_alpha()
        self.image = pg.transform.scale(self.image, (self.diameter * 2, self.diameter * 2))

        # координаты шашки в pygame
        self.rectangle = (self.center[0] - self.diameter, self.center[1] - self.diameter,
                          self.diameter * 2, self.diameter * 2)

    def draw(self, time_delta):
        pg.draw.circle(self.parent_surface, self.color, self.center, self.diameter, 0)
        if self.selected:
            shine_pos = self.rectangle[0] - self.shine_range, self.rectangle[1] - self.shine_range
            self.parent_surface.blit(self.shine, shine_pos)

        self.parent_surface.blit(self.image, (self.rectangle[0], self.rectangle[1]))


class Board:
    def __init__(self, parent_surface: pg.Surface, board_size: (int, int), indentations: (int, int), dir_path):
        self.indentations = indentations
        self.dir_path = dir_path
        self.parent_surface = parent_surface
        self.width, self.height = board_size

        self.markup = []
        self.borders_size = 15
        upper_border = pg.Surface((self.width, self.borders_size))
        lower_border = pg.Surface((self.width, self.borders_size))
        upper_border.fill('#572A00')
        lower_border.fill('#572A00')
        self.markup.append((upper_border, (indentations[0], indentations[1])))
        self.markup.append((lower_border, (indentations[0], indentations[1] + self.height - self.borders_size)))

        right_border = pg.Surface((self.borders_size, self.height - self.borders_size * 2))
        right_border.fill('#572A00')
        self.markup.append((right_border, (indentations[0], indentations[1] + self.borders_size)))

        left_border = pg.Surface((self.borders_size, self.height - self.borders_size * 2))
        left_border.fill('#572A00')
        self.markup.append(
            (left_border, (indentations[0] + self.width - self.borders_size, indentations[1] + self.borders_size)))

        field_size = self.width - self.borders_size * 2, self.height - self.borders_size * 2

        # сколько полей в строке и столбце
        rang = 8
        self.rang = rang
        self.cell_size = field_size[0] / rang, field_size[1] / rang
        self.cells: (int, int, pg.Surface) = list()

        # x - вертикали! y - горизонтали! Начало в верхнем левом углу
        for x in range(1, rang + 1):
            for y in range(1, rang + 1):
                color = 'White'
                if (8 - x + 8 - y) % 2 != 0:
                    color = '#321B00'  # черно-каштановый
                cell = pg.Surface(self.cell_size)
                cell.fill(color)
                pos = indentations[0] + self.borders_size + self.cell_size[0] * (x - 1), indentations[
                    1] + self.borders_size + self.cell_size[1] * (y - 1)
                self.markup.append((cell, pos))
                self.cells.append((x, y, cell))

        self.black_line = 1
        self.white_line = rang

        self.selected_checker = None
        self.checkers: list[Checker] = list()

        # заготовка для создания руки
        self.hand = pg.image.load(os.path.join(self.dir_path, 'Assets/Images/punch.png')).convert_alpha()
        self.hand_size = 54, 40  # исходя из размера png
        self.hand = pg.transform.scale(self.hand, self.hand_size)
        self.point_angle = None
        self.punch_coordinats = None

    def start_new_game(self):
        self.black_line = 1
        self.white_line = self.rang
        self.fill_checkers()

    def draw(self, time_delta):
        for element in self.markup:
            self.parent_surface.blit(*element)
        for checker in self.checkers:
            checker.draw(time_delta)

        if self.point_angle:
            hand, pos = self.hand_to_checker(self.selected_checker)
            self.parent_surface.blit(hand, pos)

    def hand_to_checker(self, checker):
        ch_center = checker.center
        degree, rads, x, y = calculate_point_diffs(ch_center, self.point_angle)
        rotated_hand = pg.transform.rotate(self.hand, degree)  # минусовой градус для правильного оффсета
        if (degree > 165) and (degree < 195):
            rotated_hand = pg.transform.flip(rotated_hand, False, True)

        # на сколько рука удалена от центра шашки
        offset = pg.math.Vector2(checker.diameter * 1.9, 0).rotate(-degree)
        pos = rotated_hand.get_rect(center=checker.center + offset)

        return rotated_hand, pos

    def fill_checkers(self):
        if len(self.checkers) != 0:
            self.checkers.clear()

        for x in range(self.rang + 1):
            for cell in self.cells:
                if cell[0] == x:
                    center_tur = cell[2].get_rect().center
                    if cell[1] == self.black_line:
                        center = self.indentations[0] + self.borders_size + center_tur[0] + self.cell_size[0] * (x - 1), \
                                 self.indentations[1] + self.borders_size + \
                                 center_tur[1] + \
                                 self.cell_size[1] * (self.black_line - 1)
                        new = Checker(self.parent_surface, center, 1, 25, Checker.Color.Black, self.dir_path)
                        self.checkers.append(new)
                    elif cell[1] == self.white_line:
                        center = self.indentations[0] + self.borders_size + center_tur[0] + self.cell_size[0] * (x - 1), \
                                 self.indentations[1] + self.borders_size + \
                                 center_tur[1] + \
                                 self.cell_size[1] * (self.white_line - 1)
                        new = Checker(self.parent_surface, center, 1, 25, Checker.Color.White, self.dir_path)
                        self.checkers.append(new)

    def process_click(self, pos: (int, int)):
        for checker in self.checkers:
            collision = pg.Rect(*checker.rectangle).collidepoint(pos)
            if collision:
                # Алгоритм: Выясняем, попало ли значение в круг

                # Находим абсолютные значения координаты точки относительно центра
                tested_point = abs(pos[0] - checker.center[0]), abs(pos[1] - checker.center[1])
                # Используем теорему Пифагора
                distance = math.sqrt(math.pow(tested_point[0], 2) + math.pow(tested_point[1], 2))
                # Если расстояние меньше диаметра, то шашка нажата
                if distance <= checker.diameter:
                    if checker.selected:
                        checker.selected = False
                        self.selected_checker = None
                    else:
                        if self.selected_checker:
                            self.selected_checker.selected = False
                        checker.selected = True
                        self.selected_checker = checker
                    # убираем руку при изменении выбранной шашки
                    self.point_angle = None
                    # return чтобы не проходил elif дальше по коду
                    return
            elif self.selected_checker:
                self.point_angle = pos


if __name__ == '__main__':
    pg.init()
    RES = 660, 720
    board_size = 550, 550
    indentations = (RES[0] - board_size[0]) / 2, (RES[0] - board_size[1]) / 2

    display = pg.display.set_mode((1000, 1000))
    display.fill('White')
    game_surface = pg.Surface(RES)
    game_surface.fill('#DECAFF')

    DIR = r"D:\Ukron Studio\ChapaevGame"

    board = Board(game_surface, board_size, indentations, DIR)

    Board.start_new_game(board)

    loop = True
    timer = pg.time.Clock()
    dt = 0

    while loop:

        display.blit(game_surface, indentations)
        game_surface.fill('#DECAFF')
        board.draw(dt)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                loop = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    board_rect = game_surface.get_rect(topleft=indentations)
                    if board_rect.collidepoint(event.pos):
                        board.process_click((event.pos[0] - indentations[0], event.pos[1] - indentations[1]))

        pg.display.flip()
        dt = timer.tick(100) / 1000
