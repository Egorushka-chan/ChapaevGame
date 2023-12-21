import os
import math
from enum import Enum

import pygame as pg

from Modules.Compute import ComputeTable

MAX_FORCE = 10.0


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


class Color(Enum):
    Black = 0
    White = 1
    Non = 2


class Checker:
    def __init__(self, parent_surface, center: (int | float, int | float), mass, radius, side: Color, dir_path, id):
        self.id = id
        self.dir_path = dir_path
        self.center = center
        self.side: Color = side
        self.radius = radius
        self.mass = mass
        self.parent_surface = parent_surface

        # выбор шашки и её свечение при этом
        self.selected: bool = False
        self.shine = pg.image.load(os.path.join(self.dir_path, 'Assets/Images/shine.png')).convert_alpha()
        self.shine_range = 10
        self.shine = pg.transform.scale(self.shine, (
            (self.radius + self.shine_range) * 2, (self.radius + self.shine_range) * 2))

        # цвет обводки и спрайт шашки
        self.fill = ''
        if self.side == Color.White:
            self.fill = "White"
            image_path = os.path.join(self.dir_path, 'Assets/Images/white_checker.png')
        else:
            self.fill = "Black"
            image_path = os.path.join(self.dir_path, 'Assets/Images/black_checker.png ')
        self.image = pg.image.load(image_path).convert_alpha()
        self.image = pg.transform.scale(self.image, (self.radius * 2, self.radius * 2))

        # координаты шашки в pygame
        self.rectangle = (self.center[0] - self.radius, self.center[1] - self.radius,
                          self.radius * 2, self.radius * 2)

    def draw(self, time_delta):
        pg.draw.circle(self.parent_surface, self.fill, self.center, self.radius, 0)
        if self.selected:
            shine_pos = self.rectangle[0] - self.shine_range, self.rectangle[1] - self.shine_range
            self.parent_surface.blit(self.shine, shine_pos)

        self.rectangle = (self.center[0] - self.radius, self.center[1] - self.radius,
                          self.radius * 2, self.radius * 2)
        self.parent_surface.blit(self.image, (self.rectangle[0], self.rectangle[1]))


class ForceSkillChoicer:
    def __init__(self, parent_surface):
        self.parent_surface = parent_surface
        self.visible = False
        self.size = 72, 48

        self.pos: [int, int] = 0, 0
        self.selection_line_pos = 0
        self.selection_line_direction = 1
        self.speed = MAX_FORCE * 3  # дистанция силы в секунду

        self.elements_count = 7

        self.selection_line = pg.Surface((self.size[0] / (self.elements_count * 2), self.size[1]))

    def create_lines(self):
        lines = []
        weak_color = '#4DFF00'
        mod_color = '#00FFFF'
        hard_color = '#AB00FF'
        max_color = '#FF0000'
        elements_width = self.size[0] / (self.elements_count * 2)
        elements_start_height = self.size[1] / 2
        elements_append_height = (self.size[1] - elements_start_height) / self.elements_count
        force_per_element = MAX_FORCE / self.elements_count
        for i in range(1, self.elements_count + 1):
            line = pg.Surface((elements_width, elements_start_height + elements_append_height * i))
            line_force = force_per_element * i
            line_color = weak_color
            if line_force > MAX_FORCE / 4:
                line_color = mod_color
            if line_force > MAX_FORCE / 2:
                line_color = hard_color
            if line_force > MAX_FORCE / 1.1:
                line_color = max_color
            line.fill(line_color)
            pos = self.pos[0] + elements_width * ((i - 1) * 2), self.pos[1] + (elements_append_height * (7 - i)) / 2
            lines.append((line, pos))
        line = pg.Surface((elements_width, self.size[1]))
        line.fill(max_color)
        lines.append((line, (self.pos[0] + self.size[0], self.pos[1])))
        return lines

    def append(self, pos):
        self.pos = pos
        self.visible = True

    def hide(self):
        self.visible = False

    def draw_line(self, evolve):
        self.selection_line_pos = self.selection_line_pos + (self.speed * evolve) * self.selection_line_direction
        if self.selection_line_pos > MAX_FORCE:
            self.selection_line_pos = MAX_FORCE
            self.selection_line_direction = -1
        elif self.selection_line_pos < 0:
            self.selection_line_pos = 0
            self.selection_line_direction = 1
        line_pos = self.pos[0] + self.size[0] * (self.selection_line_pos / MAX_FORCE), self.pos[1]
        self.parent_surface.blit(self.selection_line, line_pos)

    def draw(self, time_delta):
        lines = self.create_lines()
        for line in lines:
            self.parent_surface.blit(*line)
        self.draw_line(time_delta)

    def get(self) -> float:
        return self.selection_line_pos


class Board:
    def __init__(self, parent_surface: pg.Surface, board_size: (int, int), indentations: (int, int), dir_path):
        self.indentations = indentations
        self.dir_path = dir_path
        self.parent_surface = parent_surface
        self.size = self.width, self.height = board_size
        self.compute_table: ComputeTable = None

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

        # код для текущего состояния доски
        self.black_line = 1
        self.white_line = rang
        self.round = 1
        self.current_step: Color = Color.White
        self.removed_opposite = False

        # код для хранения шашек
        self.selected_checker = None
        self.checkers: list[Checker] = list()

        # код для создания руки
        self.hand = pg.image.load(os.path.join(self.dir_path, 'Assets/Images/punch.png')).convert_alpha()
        self.hand_size = 54, 40  # исходя из размера png
        self.hand = pg.transform.scale(self.hand, self.hand_size)
        self.point_angle = None
        self.punch_coordinates: [int, int] = 0, 0

        # код для зажатой мыши
        self.force_choicer = ForceSkillChoicer(self.parent_surface)

    def start_new_game(self):
        self.black_line = 1
        self.white_line = self.rang
        self.fill_checkers()

    def continue_game(self, victory_side: Color):
        if victory_side == Color.White:
            self.white_line -= 1
            if self.white_line <= self.black_line:
                self.black_line = self.white_line - 1
            self.current_step = Color.White
        if victory_side == Color.Black:
            self.black_line += 1
            if self.black_line <= self.white_line:
                self.white_line = self.black_line + 1
            self.current_step = Color.Black
        if victory_side == Color.Non:
            if self.black_line != 1:
                self.black_line -= 1
            if self.white_line != self.rang:
                self.white_line += 1
            self.current_step = Color.White
        self.fill_checkers()

    def draw(self, time_delta):
        for element in self.markup:
            self.parent_surface.blit(*element)
        if not self.compute_table:
            for checker in self.checkers:
                checker.draw(time_delta)

            if self.point_angle:
                hand, pos = self.hand_to_checker(self.selected_checker)
                self.parent_surface.blit(hand, pos)

            if self.force_choicer.visible:
                self.force_choicer.draw(time_delta)
        else:
            result, status = self.compute_table.evolve(time_delta)
            non_appeared_checkers: list[Checker] = self.checkers.copy()
            for result_checker in result:
                for element_checker in self.checkers:
                    if result_checker.id == element_checker.id:
                        element_checker.center = result_checker.pos
                        non_appeared_checkers.remove(element_checker)

            for checker in non_appeared_checkers:
                if self.current_step != checker.side:
                    self.removed_opposite = True
                self.checkers.remove(checker)

            for checker in self.checkers:
                checker.draw(time_delta)
            if not status:
                self.compute_table = None
                if self.removed_opposite:
                    self.removed_opposite = False
                else:
                    if self.current_step == Color.White:
                        self.current_step = Color.Black
                    else:
                        self.current_step = Color.White

    def hand_to_checker(self, checker):
        ch_center = checker.center
        degree, rads, x, y = calculate_point_diffs(ch_center, self.point_angle)
        self.punch_coordinates = x, y
        rotated_hand = pg.transform.rotate(self.hand, degree)  # минусовой градус для правильного оффсета
        if (degree > 165) and (degree < 195):
            rotated_hand = pg.transform.flip(rotated_hand, False, True)

        # на сколько рука удалена от центра шашки
        offset = pg.math.Vector2(checker.radius * 1.9, 0).rotate(-degree)
        pos = rotated_hand.get_rect(center=checker.center + offset)

        return rotated_hand, pos

    def fill_checkers(self):
        if len(self.checkers) != 0:
            self.checkers.clear()

        id = 0
        for x in range(self.rang + 1):
            for cell in self.cells:
                if cell[0] == x:
                    center_tur = cell[2].get_rect().center
                    if cell[1] == self.black_line:
                        center = self.indentations[0] + self.borders_size + center_tur[0] + self.cell_size[0] * (x - 1), \
                                 self.indentations[1] + self.borders_size + \
                                 center_tur[1] + \
                                 self.cell_size[1] * (self.black_line - 1)
                        new = Checker(self.parent_surface, center, 0.100, 25, Color.Black, self.dir_path, id)
                        self.checkers.append(new)
                        id += 1
                    elif cell[1] == self.white_line:
                        center = self.indentations[0] + self.borders_size + center_tur[0] + self.cell_size[0] * (x - 1), \
                                 self.indentations[1] + self.borders_size + \
                                 center_tur[1] + \
                                 self.cell_size[1] * (self.white_line - 1)
                        new = Checker(self.parent_surface, center, 0.100, 25, Color.White, self.dir_path, id)
                        self.checkers.append(new)
                        id += 1

    def process_click(self, pos: (int, int)):
        if self.compute_table is None:
            for checker in self.checkers:
                collision = pg.Rect(*checker.rectangle).collidepoint(pos)
                if collision:
                    # Алгоритм: Выясняем, попало ли значение в круг

                    # Находим абсолютные значения координаты точки относительно центра
                    tested_point = abs(pos[0] - checker.center[0]), abs(pos[1] - checker.center[1])
                    # Используем теорему Пифагора
                    distance = math.sqrt(math.pow(tested_point[0], 2) + math.pow(tested_point[1], 2))
                    # Если расстояние меньше диаметра, то шашка нажата
                    if distance <= checker.radius:
                        if not self.force_choicer.visible:
                            if checker.selected:
                                checker.selected = False
                                self.selected_checker = None
                            else:
                                if self.selected_checker:
                                    self.selected_checker.selected = False
                                if self.current_step == checker.side:
                                    print(checker.center)
                                    checker.selected = True
                                    self.selected_checker = checker
                            # убираем руку при изменении выбранной шашки
                            self.point_angle = None
                            # return чтобы не проходил elif дальше по коду
                            return
                elif self.selected_checker:
                    self.point_angle = pos

    def process_handling(self, pos, button_type):
        if self.point_angle:
            if button_type == 1:
                self.point_angle = pos
                return

    def forcing(self, state, pos):
        if self.point_angle:
            if state:
                self.force_choicer.append(pos)
            else:
                self.force_choicer.hide()
                self.point_angle = None
                force = self.force_choicer.get()
                id = self.selected_checker.id
                self.selected_checker.selected = False
                self.selected_checker = None
                self.punch(force, self.punch_coordinates, id)

    def punch(self, force: float, punch_coordinates: [int, int], id):
        punch_coordinates = punch_coordinates[0] * -1, punch_coordinates[1]
        print(f'Совершен удар по {id}: сила = {force}; направление = {punch_coordinates}')
        rect = self.parent_surface.get_rect(topleft=self.indentations)
        self.compute_table = ComputeTable(rect.topleft, rect.bottomright)
        for checker in self.checkers:
            id_cheker = checker.id
            radius = checker.radius
            mass = checker.mass
            pos = checker.center
            if id == id_cheker:
                velocity = punch_coordinates[0] * (force / mass), punch_coordinates[1] * (force / mass)
            else:
                velocity = [0, 0]
            self.compute_table.add_ball(id_cheker, radius, mass, pos, velocity)

    def check_victory(self):
        is_whites = False
        is_blacks = False
        for checker in self.checkers:
            if checker.side == Color.White:
                is_whites = True
            if checker.side == Color.Black:
                is_blacks = True

        if is_whites and not is_blacks:
            self.continue_game(Color.White)
            return f'Победа белых в раунде {self.round}'
        if is_blacks and not is_whites:
            self.continue_game(Color.Black)
            return f'Победа чёрных в раунде {self.round}'


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
            board_rect = game_surface.get_rect(topleft=indentations)
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if board_rect.collidepoint(event.pos):
                        board.process_click((event.pos[0] - indentations[0], event.pos[1] - indentations[1]))
            else:
                if pg.mouse.get_pressed()[0]:
                    if board_rect.collidepoint(event.pos):
                        board.process_handling((event.pos[0] - indentations[0], event.pos[1] - indentations[1]), 1)

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 3 and board_rect.collidepoint(event.pos):
                board.forcing(True, (event.pos[0] - indentations[0], event.pos[1] - indentations[1]))
            elif event.type == pg.MOUSEBUTTONUP and event.button == 3 and board.force_choicer.visible:
                board.forcing(False, (event.pos[0] - indentations[0], event.pos[1] - indentations[1]))

        pg.display.flip()
        dt = timer.tick(100) / 1000
