import copy

from Modules.Compute import ComputeTable, ComputeBall
from Modules.Board import MAX_FORCE, calculate_point_diffs
from pygame import Rect


class BotPlayer:
    def __init__(self, checkers_id: [int], size, topleft, side):
        self.topleft = topleft
        self.size = size
        self.my_checkers_id = checkers_id
        self.side = side

    def get_step_choice(self, table: ComputeTable):
        possible_forces = [3, MAX_FORCE]

        my_balls = []
        for ball in table.balls:
            if ball.id in self.my_checkers_id:
                my_balls.append(ball)

        possible_strikes = []
        for my_ball in my_balls:
            for all_ball in table.balls:
                if my_ball.id != all_ball.id:
                    degs, rads, x, y = calculate_point_diffs(all_ball.pos, my_ball.pos)
                    punch_dir = x * -1, y
                    for force in possible_forces:
                        velocity = punch_dir[0] * force / my_ball.mass, punch_dir[1] * force / my_ball.mass
                        possible_strikes.append([my_ball.id, velocity])

        best_strike = None
        max_score = 0

        table_copy = copy.deepcopy(table)
        for my_copy_ball in table_copy.balls:
            for strike in possible_strikes:
                my_id, vel = strike
                if my_copy_ball.id == my_id:
                    my_copy_ball.velocity = vel
                    placement, _ = copy.deepcopy(table_copy).compute()
                    my_copy_ball.velocity = [0, 0]
                    result = self.evaluation_function(placement)
                    if best_strike is None:
                        best_strike = strike
                        max_score = result
                    else:
                        if result > max_score:
                            best_strike = strike
                            max_score = result
        return best_strike

    def evaluation_function(self, balls):
        result = 0  # положительное это преймущество бота
        for ball in balls:
            center = Rect(0, 0, self.size[0], self.size[1]).center
            border_disadvantage = 0
            if self.topleft[0] + 100 > ball.pos[0]:
                border_disadvantage += 0.1
            if self.topleft[1] + 100 > ball.pos[1]:
                border_disadvantage += 0.1
            if self.topleft[0] + self.size[0] - 100 < ball.pos[0]:
                border_disadvantage += 0.1
            if self.topleft[1] + self.size[1] - 100 < ball.pos[1]:
                border_disadvantage += 0.1

            if ball.id in self.my_checkers_id:
                result += 2 - border_disadvantage
            else:
                result -= 2 + border_disadvantage
        return result
