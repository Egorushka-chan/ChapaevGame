from Compute import ComputeTable
from Board import MAX_FORCE, calculate_point_diffs


class BotPlayer:
    def __init__(self, checkers_id: [int], topleft, bottomright):
        self.table_size = topleft, bottomright
        self.my_checkers_id = []

    def get_step_choice(self):
        possible_forces = [3, MAX_FORCE]
        is_killed_enemy_checker = True  # True он сейчас, чтобы зайти в цикл первый раз
        table = ComputeTable(*self.table_size)

        while is_killed_enemy_checker:
            is_killed_enemy_checker = False

            possible_moves = []
            my_balls = []
            for ball in table.balls:
                if ball.id in self.my_checkers_id:
                    my_balls.append(ball)

            for my_ball in my_balls:

                for all_ball in table.balls:
                    if my_ball.id != all_ball:
                        degs, rads, x, y = calculate_point_diffs(my_ball.pos, all_ball.pos)
                        punch_dir = x*-1, y


    def evaluation_function(self):
        """
        Оценочная функция оценивает положение сторон на основании того, сколько шашек у сторон и насколько близко они
        находятся к центру карты.
        :return: в
        """
        pass
