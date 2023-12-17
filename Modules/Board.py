import pygame as pg


class Checker:
    def __init__(self, parent_surface, mass, diameter):
        pass

    def draw(self, time_delta):
        pass

    def collide_checker(self, checker):
        pass


class Board:
    def __init__(self, parent_surface: pg.Surface):
        self.parent_surface = parent_surface
        self.width, self.height = self.parent_surface.get_size()

        self.checkers: list[Checker] = list()

        self.markup = []
        borders_size = 15
        upper_border = pg.Surface((self.width, borders_size))
        lower_border = pg.Surface((self.width, borders_size))
        upper_border.fill('#572A00')
        lower_border.fill('#572A00')
        self.markup.append((upper_border, (0, 0)))
        self.markup.append((lower_border, (0, self.height - borders_size)))

        right_border = pg.Surface((borders_size, self.height - borders_size * 2))
        right_border.fill('#572A00')
        self.markup.append((right_border, (0, borders_size)))

        left_border = pg.Surface((borders_size, self.height - borders_size * 2))
        left_border.fill('#572A00')
        self.markup.append((left_border, (self.width - borders_size, borders_size)))

        field_size = self.width - borders_size * 2, self.height - borders_size * 2

        # сколько полей в строке и столбце
        rang = 8
        cell_size = field_size[0] / rang, field_size[1] / rang
        self.cells: (int, int, pg.Surface) = []

        # x - вертикали! y - горизонтали! Начало в верхнем левом углу
        for x in range(1, rang + 1):
            for y in range(1, rang + 1):
                color = 'White'
                if (8-x + 8-y) % 2 != 0:
                    color = '#321B00'  # черно-каштановый
                cell = pg.Surface(cell_size)
                cell.fill(color)
                pos = borders_size + cell_size[0] * (x - 1), borders_size + cell_size[1] * (y - 1)
                self.markup.append((cell, pos))

    def draw(self, time_delta):
        for element in self.markup:
            self.parent_surface.blit(*element)

    def evolve(self, time_delta):
        pass


if __name__ == '__main__':
    pg.init()
    RES = 1000, 1000
    display = pg.display.set_mode(RES)
    display.fill('White')
    surface = pg.Surface((500, 500))
    surface.fill('#DECAFF')
    board = Board(surface)

    loop = True
    timer = pg.time.Clock()
    dt = 0

    while loop:

        display.blit(surface, (250, 250))
        board.draw(dt)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                loop = False

        pg.display.flip()
        dt = timer.tick(100) / 1000
