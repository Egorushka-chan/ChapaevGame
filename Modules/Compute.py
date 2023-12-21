from datetime import datetime
import math

import numpy as np

BALL_FRICTION = 0.54
EARTH_FORCE = 9.807
INF = float("inf")


def calculate_trigonometry(x, y):
    rads = math.atan2(y, x)
    rads %= 2 * math.pi
    degs = math.degrees(rads)
    x = abs(math.cos(rads))
    y = abs(math.sin(rads))
    return degs, rads, x, y


def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0


def N(mass):
    return mass * EARTH_FORCE


def friction_force(mass):
    return BALL_FRICTION * N(mass)


def deceleration(mass):
    return friction_force(mass) / mass


class ComputeBall:
    def __init__(self, id, radius, mass, pos, velocity):
        self.id = id
        self.pos = pos
        self.mass = mass
        self.radius = radius
        self.velocity = velocity

        self.stop_time = 0

        self.calc_stop_time()

    def calc_stop_time(self):
        vel = np.sqrt(np.dot(self.velocity, self.velocity))
        dec = deceleration(self.mass)
        return vel / dec


class ComputeTable:
    def __init__(self, topleft, bottomright):
        self.bottomright = bottomright
        self.topleft = topleft
        self.balls: list[ComputeBall] = []
        self.end_time = 0
        self.end_positions: list[ComputeBall] = []
        self.kicked_balls = []

    def add_ball(self, id, radius, mass, pos, velocity):
        ball = ComputeBall(id, radius, mass, pos, velocity)
        self.balls.append(ball)

    def evolve(self, dt):
        movable_balls = []
        for ball in self.balls:
            if (ball.velocity[0] != 0) or (ball.velocity[1] != 0):
                movable_balls.append(ball)
        collisions = []
        for mv_b in movable_balls:
            for ball in self.balls:
                if mv_b != ball:
                    imp_time = self.time_of_impact(mv_b, ball)
                    if imp_time != INF:
                        if (imp_time, ball, mv_b) not in collisions:
                            collisions.append((imp_time, mv_b, ball))
        if len(collisions) > 0:
            min_time = INF
            for collision in collisions:
                imp_time, mv_b, ball = collision
                min_time = min(min_time, imp_time)
            if min_time < dt:
                for collision in collisions:
                    imp_time, mv_b, ball = collision
                    if min_time == imp_time:
                        new_vels = self.elastic_collision(mv_b, ball)
                        self.move(mv_b, imp_time)
                        # self.move(ball, imp_time)
                        mv_b.velocity, ball.velocity = new_vels

        for ball in self.balls:
            if (ball.velocity[0] != 0) or (ball.velocity[1] != 0):
                self.move(ball, dt)

        # out_of_range_balls = []
        # for ball in self.balls:
        #     if (ball.pos[0] < 0) or (ball.pos[0] < 0) or (ball.pos[0] > self.size[0]) or (ball.pos[1] > self.size[1]):
        #         out_of_range_balls.append(ball)
        # for ball in out_of_range_balls:
        #     self.balls.remove(ball)

        movable_balls.clear()
        movable_balls = []
        for ball in self.balls:
            if (ball.velocity[0] != 0) or (ball.velocity[1] != 0):
                movable_balls.append(ball)
        status = True
        if len(movable_balls) == 0:
            status = False
        return self.balls, status

    def compute(self):
        result = self.recur(self.balls.copy())
        return result

    def recur(self, balls, dt=0, total_time=0):
        if dt:
            for ball in balls:
                if (ball.velocity[0] != 0) or (ball.velocity[1] != 0):
                    self.move(ball, dt)

        movable_balls = []
        for ball in balls:
            if (ball.velocity[0] != 0) or (ball.velocity[1] != 0):
                movable_balls.append(ball)

        collisions = []
        for mv_b in movable_balls:
            for ball in balls:
                if mv_b != ball:
                    imp_time = self.time_of_impact(mv_b, ball)
                    if imp_time != INF:
                        if (imp_time, ball, mv_b) not in collisions:
                            collisions.append((imp_time, mv_b, ball))
        if len(collisions) > 0:
            min_time = INF
            for collision in collisions:
                imp_time, mv_b, ball = collision
                min_time = min(min_time, imp_time)
            for collision in collisions:
                imp_time, mv_b, ball = collision
                if min_time == imp_time:
                    new_vels = self.elastic_collision(mv_b, ball)
                    self.move(mv_b, imp_time)
                    mv_b.velocity, ball.velocity = new_vels
                    total_time += min_time
                    dt = min_time
        else:
            max_time = 0
            for ball in balls:
                test_time = ball.calc_stop_time()
                if (ball.velocity[0] != 0) or (ball.velocity[1] != 0):
                    self.move(ball, test_time)
                max_time = max(max_time, test_time)
                total_time = total_time + max_time
            return balls, total_time

        return self.recur(balls.copy(), dt, total_time)

    def move(self, ball: ComputeBall, dt):
        new_pos = [ball.pos[0], ball.pos[1]]
        new_velocity = [0, 0]

        total_vel = abs(ball.velocity[0]) + abs(ball.velocity[1])
        vel1_scale = abs(ball.velocity[0]) / total_vel
        vel2_scale = abs(ball.velocity[1]) / total_vel

        decel = deceleration(ball.mass)
        a, rads, cos_a, sin_a = calculate_trigonometry(ball.velocity[0], ball.velocity[1])

        total_vector_velocity = abs(ball.velocity[0] * cos_a) + abs(ball.velocity[1] * sin_a)
        # total_path = math.sqrt(abs(ball.velocity[0] * dt) ** 2 + abs(ball.velocity[1] * dt) ** 2)
        # total_path_friction = deceleration(ball.mass) * dt

        if total_vector_velocity > decel:
            stop_time = ball.calc_stop_time()
            if stop_time < dt:
                dt = stop_time



            # не подходит, при маленьком значении одной скорости при большой другой (пример: (2, 102)) и тд,
            # на большой дельте времени эта двойка из примера уходила по дуге в противоположную сторону
            # if ball.velocity[0] != 0:
            #     new_pos[0] = ball.pos[0] + ball.velocity[0] * dt - (decel * (dt ** 2)) / 2
            # if ball.velocity[1] != 0:
            #     new_pos[1] = ball.pos[1] + ball.velocity[1] * dt - (decel * (dt ** 2)) / 2

            # Решение: находим время до предполагаемого конца пути. Там наша двойка 100% будет 0, а затем аппроксимируем
            # это время на нашу дельту времени

            # end_pos = (ball.pos[0] + ball.velocity[0] * stop_time - (decel * (stop_time ** 2) * vel1_scale) / 2,
            #            ball.pos[1] + ball.velocity[1] * stop_time - (decel * (stop_time ** 2)* vel2_scale) / 2)
            paths = stop_time / dt
            path_velocity_step = ball.velocity[0] / paths, ball.velocity[1] / paths
            # path_pos_step = end_pos[0] / paths, end_pos[1]/ paths
            new_velocity = ball.velocity[0] - path_velocity_step[0], ball.velocity[1] - path_velocity_step[1]
            new_pos = (ball.pos[0] + ball.velocity[0] * dt * cos_a - (decel * (dt ** 2)) * cos_a / 2,
                       ball.pos[1] + ball.velocity[1] * dt * sin_a - (decel * (dt ** 2)) * sin_a / 2)

            i = 1

            # if ball.velocity[0] == 0:
            #     assert new_pos[0] == ball.pos[0], 'Шашка переместилась без скорости по 0'
            # if ball.velocity[1] == 0:
            #     assert new_pos[1] == ball.pos[1], 'Шашка переместилась без скорости по 1'

            # new_velocity[0] = ball.velocity[0] - decel * dt * signs_vel[0] * vel1_scale
            # if abs(new_velocity[0]) > abs(ball.velocity[0]):
            #     assert abs(new_velocity[0]) > abs(ball.velocity[0]), (f'Шашка {ball.id} ускорилась при движении по 0, '
            #                                                           f'стр_скр: {ball.velocity[0]}, '
            #                                                           f'нов_вел: {new_velocity[0]}, '
            #                                                           f'зам= {decel}, '
            #                                                           f'dt= {dt}, '
            #                                                           f'sign={signs_vel[0]}, '
            #                                                           f'vel1_scale={vel1_scale}')
            #
            # new_velocity[1] = ball.velocity[1] - decel * dt * signs_vel[1] * vel2_scale
            # if abs(new_velocity[1]) > abs(ball.velocity[1]):
            #     assert abs(new_velocity[1]) > abs(ball.velocity[1]), (f'Шашка {ball.id} ускорилась при движении по 1, '
            #                                                           f'стр_скр: {ball.velocity[1]}, '
            #                                                           f'нов_скр: {new_velocity[1]}, '
            #                                                           f'зам= {decel}, '
            #                                                           f'dt= {dt}, '
            #                                                           f'sign={signs_vel[1]}, '
            #                                                           f'vel1_scale={vel2_scale}')

        # версия движения 1.0
        # if abs(ball.velocity[0]) > decel:
        #     new_pos[0] = ball.pos[0] + ball.velocity[0] * dt + (decel * (dt ** 2)) / 2
        # if abs(ball.velocity[1]) > decel:
        #     new_pos[1] = ball.pos[1] + ball.velocity[1] * dt + (decel * (dt ** 2)) / 2
        # if abs(ball.velocity[0]) > decel:
        #     if ball.velocity[0] < 0:
        #         new_velocity[0] = ball.velocity[0] + decel * dt
        #     else:
        #         new_velocity[0] = ball.velocity[0] - decel * dt
        # if abs(ball.velocity[1]) > decel:
        #     if ball.velocity[1] < 0:
        #         new_velocity[1] = ball.velocity[1] + decel * dt
        #     else:
        #         new_velocity[1] = ball.velocity[1] - decel * dt
        ball.velocity = new_velocity
        ball.pos = new_pos

        # for ball in self.balls:
        #     if (ball.pos[0] < self.topleft[0]) or (ball.pos[1] < self.topleft[1]) or (
        #             ball.pos[0] > self.bottomright[0] - self.topleft[0]) or (
        #             ball.pos[1] > self.bottomright[1] - self.topleft[1]):
        #         self.kicked_balls.append(ball)
        #     for ball in self.kicked_balls:
        #         if ball in self.balls:
        #             self.balls.remove(ball)

    def elastic_collision(self, first_ball: ComputeBall, second_ball: ComputeBall):
        pos_diff = np.subtract(second_ball.pos, first_ball.pos)
        vel_diff = np.subtract(second_ball.velocity, first_ball.velocity)

        pos_dot_vel = pos_diff.dot(vel_diff)
        assert pos_dot_vel < 0

        dist_sqrd = pos_diff.dot(pos_diff)

        bla = 2 * (pos_dot_vel * pos_diff) / ((first_ball.mass + second_ball.mass) * dist_sqrd)
        vel1 = first_ball.velocity + (second_ball.mass * bla) / 1.5
        vel2 = second_ball.velocity - (first_ball.mass * bla) / 1.5
        return vel1, vel2

    def time_of_impact(self, first_ball: ComputeBall, second_ball: ComputeBall):
        pos_diff = np.subtract(second_ball.pos, first_ball.pos)
        vel_diff = np.subtract(second_ball.velocity, first_ball.velocity)

        # проверка, если они двигаются в разные стороны
        pos_dot_vel = pos_diff.dot(vel_diff)
        if pos_dot_vel >= 0:
            return INF

        # Формула состоит в том, что бы высчитать время столкновения по дискриминанту:
        # a*t^2 + 2*u0*t + s = 0 => ax^2 + bx + c = 0
        vel_sqrd = math.sqrt(vel_diff.dot(vel_diff))
        b = vel_sqrd * 2
        c = 2 * (math.sqrt(pos_diff[0] ** 2 + pos_diff[1] ** 2) - first_ball.radius - second_ball.radius)
        a = deceleration(first_ball.mass)
        discriminant = b ** 2 - 4 * a * c
        if discriminant <= 0:
            # они не попадут
            return INF

        t1 = (-b + math.sqrt(discriminant)) / (2 * a)
        t2 = (-b - math.sqrt(discriminant)) / (2 * a)

        return min(-t1, -t2)


if __name__ == '__main__':
    # тестирование работы двух методов: априорного и апостериорного:
    res = []
    res.append(calculate_trigonometry(1, 0))
    res.append(calculate_trigonometry(0, 1))
    res.append(calculate_trigonometry(1, 1))
    res.append(calculate_trigonometry(-1, -1))

    comp_evl = ComputeTable(topleft=(55, 55), bottomright=(715, 715))
    comp_evl.add_ball(0, 25, 0.100, (102, 102), (0, 0))
    comp_evl.add_ball(1, 25, 0.100, (167, 102), (0, 0))
    comp_evl.add_ball(2, 25, 0.100, (232, 102), (0, 0))
    comp_evl.add_ball(3, 25, 0.100, (297, 102), (0, 0))
    comp_evl.add_ball(4, 25, 0.100, (362, 102), (0, 0))
    comp_evl.add_ball(5, 25, 0.100, (427, 102), (0, 0))
    comp_evl.add_ball(6, 25, 0.100, (492, 102), (0, 0))
    comp_evl.add_ball(7, 25, 0.100, (557, 102), (0, 0))
    comp_evl.add_ball(8, 25, 0.100, (102, 557), (0, 0))
    comp_evl.add_ball(9, 25, 0.100, (167, 557), (0, 0))
    comp_evl.add_ball(10, 25, 0.100, (232, 557), (0, 0))
    comp_evl.add_ball(11, 25, 0.100, (297, 557), (0, -20))
    comp_evl.add_ball(12, 25, 0.100, (362, 557), (0, 0))
    comp_evl.add_ball(13, 25, 0.100, (427, 557), (0, 0))
    comp_evl.add_ball(14, 25, 0.100, (492, 557), (0, 0))
    comp_evl.add_ball(15, 25, 0.100, (557, 557), (0, 0))

    status = True
    time_delta = 0.01
    evolve_result = ''
    while status:
        evolve_result, status = comp_evl.evolve(time_delta)

    comp_compute = ComputeTable(topleft=(55, 55), bottomright=(715, 715))
    comp_compute.add_ball(0, 25, 0.100, (102, 102), (0, 0))
    comp_compute.add_ball(1, 25, 0.100, (167, 102), (0, 0))
    comp_compute.add_ball(2, 25, 0.100, (232, 102), (0, 0))
    comp_compute.add_ball(3, 25, 0.100, (297, 102), (0, 0))
    comp_compute.add_ball(4, 25, 0.100, (362, 102), (0, 0))
    comp_compute.add_ball(5, 25, 0.100, (427, 102), (0, 0))
    comp_compute.add_ball(6, 25, 0.100, (492, 102), (0, 0))
    comp_compute.add_ball(7, 25, 0.100, (557, 102), (0, 0))
    comp_compute.add_ball(8, 25, 0.100, (102, 557), (0, 0))
    comp_compute.add_ball(9, 25, 0.100, (167, 557), (0, 0))
    comp_compute.add_ball(10, 25, 0.100, (232, 557), (0, 0))
    comp_compute.add_ball(11, 25, 0.100, (297, 557), (0, -20))
    comp_compute.add_ball(12, 25, 0.100, (362, 557), (0, 0))
    comp_compute.add_ball(13, 25, 0.100, (427, 557), (0, 0))
    comp_compute.add_ball(14, 25, 0.100, (492, 557), (0, 0))
    comp_compute.add_ball(15, 25, 0.100, (557, 557), (0, 0))
    res = comp_compute.compute()
    for evl in evolve_result:
        for cmp in res[0]:
            if evl.id == cmp.id:
                if evl.pos != cmp.pos:
                    print(
                        f'У шашки {evl.id} не соответствует позиция: evl X={evl.pos[0]} Y={evl.pos[1]}; comp X={cmp.pos[0]} Y={cmp.pos[1]}')
                else:
                    print(
                        f'Соответствие шашки {evl.id}: evl X={evl.pos[0]} Y={evl.pos[1]}; comp X={cmp.pos[0]} Y={cmp.pos[1]}')
