import math

import numpy as np

BALL_FRICTION = 0.54
EARTH_FORCE = 9.807
INF = float("inf")


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
    def __init__(self, size):
        self.size = size
        self.balls: list[ComputeBall] = []
        self.end_time = 0
        self.end_positions: list[ComputeBall] = []
        self.collisions = []

    def add_ball(self, id, radius, mass, pos, velocity):
        ball = ComputeBall(id, radius, mass, pos, velocity)
        self.balls.append(ball)

    def compute(self):
        result = self.recur(self.balls.copy())
        print(result)

    def recur(self, balls, dt=0, total_time=0):
        if dt:
            for ball in balls:
                new_pos = self.move(ball, dt)
                ball.pos = new_pos

        movable_balls = []
        for ball in balls:
            if (ball.velocity[0] > 0) or (ball.velocity[1] > 0):
                movable_balls.append(ball)

        collisions = []
        for mv_b in movable_balls:
            for ball in balls:
                if mv_b != ball:
                    imp_time = self.time_of_impact(mv_b, ball)
                    self.collisions.append((imp_time, mv_b, ball))
        if len(collisions) > 0:
            min_time = 0
            for collision in self.collisions:
                imp_time, mv_b, ball = collision
                min_time = min(min_time, imp_time)
                self.move(mv_b, imp_time)
                self.move(ball, imp_time)
                mv_b.velocity, ball.velocity = self.elastic_collision(mv_b, ball)
                total_time += min_time
                dt = total_time - min_time
        else:
            max_time = 0
            for ball in balls:
                test_time = ball.calc_stop_time()
                self.move(ball, ball.calc_stop_time())
                max_time = max(max_time, test_time)
                total_time = total_time + max_time
                return balls, total_time

        return self.recur(balls.copy(), dt)

    def move(self, ball: ComputeBall, dt):
        new_pos = [0,0]
        new_pos[0] = ball.pos[0] + ball.velocity[0]*dt + (deceleration(ball.mass)*(dt**2))/2
        new_pos[1] = ball.pos[1] + ball.velocity[1] * dt + (deceleration(ball.mass) * (dt ** 2)) / 2

        new_velocity = [0, 0]
        if ball.velocity[0] + ball.velocity[1] > deceleration(ball.mass):
            new_velocity[0] = ball.velocity[0] - deceleration(ball.mass) * dt
            new_velocity[1] = ball.velocity[1] - deceleration(ball.mass) * dt
        ball.velocity = new_velocity
        ball.pos = new_pos

    def elastic_collision(self, first_ball: ComputeBall, second_ball: ComputeBall):
        pos_diff = np.subtract(second_ball.pos, first_ball.pos)
        vel_diff = np.subtract(second_ball.velocity, first_ball.velocity)

        pos_dot_vel = pos_diff.dot(vel_diff)
        assert pos_dot_vel < 0  # colliding balls do not move apart

        dist_sqrd = pos_diff.dot(pos_diff)

        bla = 2 * (pos_dot_vel * pos_diff) / ((first_ball.mass + second_ball.mass) * dist_sqrd)
        vel1 = first_ball.velocity + second_ball.mass * bla
        vel2 = second_ball.velocity - first_ball.mass * bla
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
    comp = ComputeTable((1000, 1000))
    comp.add_ball(1, 10, 0.100, (100, 100), (100, 100))
    comp.add_ball(2, 10, 0.100, (200, 200), (-100, 0))
    comp.add_ball(3, 10, 0.100, (10, 10), (0, 0))
    comp.add_ball(4, 10, 0.100, (300, 300), (0, 0))
    comp.add_ball(5, 10, 0.100, (500, 500), (0, 0))
    comp.compute()
