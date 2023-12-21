import math
from unittest import TestCase
from Modules.Compute import sign, ComputeTable, deceleration, ComputeBall


class TestCompute(TestCase):
    def test_signMinus(self):
        # arrange
        number = -41.142
        # act
        result = sign(number)
        # assert
        self.assertEqual(result, -1)

    def test_signPlus(self):
        # arrange
        number = 0.142
        # act
        result = sign(number)
        # assert
        self.assertEqual(result, 1)

    def test_signZero(self):
        # arrange
        number = 0
        # act
        result = sign(number)
        # assert
        self.assertEqual(result, 0)

    def test_deceleration(self):
        # arrange
        mass = 0.1
        pre_calc = 5.2958
        # act
        dec_val = round(deceleration(mass), 4)
        # result
        self.assertEqual(pre_calc, dec_val)

    def test_ComputeTable_evolve_vs_compute_difference_result(self):
        """
        Тестирование работы двух методов: априорного и апостериорного. Итоговое положение должно быть одинаковое
        """
        # arrange
        comp = ComputeTable(topleft=(55, 55), bottomright=(715, 715))
        comp.add_ball(0, 25, 0.100, (102, 102), (2, 90))
        comp.add_ball(1, 25, 0.100, (167, 102), (-10, -10))
        comp.add_ball(2, 25, 0.100, (232, 102), (0, 0))
        comp.add_ball(3, 25, 0.100, (297, 102), (0, 0))
        comp.add_ball(4, 25, 0.100, (362, 102), (2, 90))
        comp.add_ball(5, 25, 0.100, (427, 102), (0, 0))
        comp.add_ball(6, 25, 0.100, (492, 102), (0, 0))
        comp.add_ball(7, 25, 0.100, (557, 102), (0, 0))
        comp.add_ball(8, 25, 0.100, (102, 557), (0, 0))
        comp.add_ball(9, 25, 0.100, (167, 557), (0, 0))
        comp.add_ball(10, 25, 0.100, (232, 557), (-32, -44))
        comp.add_ball(11, 25, 0.100, (297, 557), (0, 0))
        comp.add_ball(12, 25, 0.100, (362, 557), (0, 0))
        comp.add_ball(13, 25, 0.100, (427, 557), (0, 0))
        comp.add_ball(14, 25, 0.100, (492, 557), (0, 0))
        comp.add_ball(15, 25, 0.100, (557, 557), (-22, -80))
        status = True
        time_delta = 0.01
        evolve_result = ''

        # act
        while status:
            evolve_result, status = comp.evolve(time_delta)
        compute_result = comp.compute()

        # assert
        cmp_result = []
        evl_result = []

        for evl in evolve_result:
            for cmp in compute_result[0]:
                if evl.id == cmp.id:
                    cmp_result.append(cmp.pos)
                    evl_result.append(evl.pos)
        self.assertEqual(cmp_result, evl_result)

    def test_ComputeTable_evolve_vs_compute_difference_move(self):
        """
        Тестирование работы двух методов: априорного и апостериорного. Итоговое положение должно быть одинаковое
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (100, 100), (150, 150))
        comp_compute = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_compute.add_ball(0, 25, 0.100, (100, 100), (150, 150))
        # act
        status = True
        time_delta = [0.004] * 10000
        evolve_result = ''
        for dt in time_delta:
            if status:
                evolve_result, status = comp_evl.evolve(dt)
        compute_result = comp_compute.compute()

        # assert
        cmp_result = []
        evl_result = []

        for evl in evolve_result:
            for cmp in compute_result[0]:
                if evl.id == cmp.id:
                    cmp_result.append((round(cmp.pos[0]), round(cmp.pos[1])))
                    evl_result.append((round(evl.pos[0]), round(evl.pos[1])))
        self.assertEqual(cmp_result, evl_result)

    def test_ComputeTable_evolve_move1(self):
        """
        Это проверка на движение по единичному значению времени
        :return:
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (102, 100), (0, 90))

        pre_calc = (102, 545)
        # act
        status = True
        time_delta = [6]
        evolve_result = ''
        for dt in time_delta:
            evolve_result, status = comp_evl.evolve(dt)

        # assert
        evl_result = []

        for evl in evolve_result:
            if evl.id == 0:
                evl_result.append((evl.pos[0], round(evl.pos[1])))
        self.assertEqual(pre_calc, evl_result[0])

    def test_ComputeTable_evolve_move2(self):
        """
        Сравнение работы через большое значение и маленькое апостериорного подхода
        """
        # arrange
        comp_evl1 = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl1.add_ball(0, 25, 0.100, (102, 100), (20, 90))

        comp_evl2 = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl2.add_ball(0, 25, 0.100, (102, 100), (20, 90))
        # act
        status = True
        time_delta = [6]
        evolve_result1 = ''
        for dt in time_delta:
            evolve_result1, status = comp_evl1.evolve(dt)

        status = True
        time_delta = [1, 1, 1, 1, 1, 1]
        evolve_result2 = ''
        for dt in time_delta:
            evolve_result2, status = comp_evl2.evolve(dt)

        # assert
        evl_result1 = []
        evl_result2 = []

        for evl in evolve_result1:
            if evl.id == 0:
                evl_result1.append((evl.pos[0], round(evl.pos[1])))
        for evl in evolve_result2:
            if evl.id == 0:
                evl_result2.append((evl.pos[0], round(evl.pos[1])))
        self.assertEqual(evl_result1, evl_result2)

    def test_ComputeTable_evolve_move1_stop_time(self):
        """
        Результат по прошествии очевидно слишком большого ОДНОГО значения времени и времени остановки должен быть одинаков
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (102, 100), (0, 90))

        comp_ball = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_ball.add_ball(0, 25, 0.100, (102, 100), (0, 90))
        stop_time = comp_ball.balls[0].stop_time
        # act
        time_delta = [10]
        evolve_result = ''
        for dt in time_delta:
            evolve_result, _ = comp_evl.evolve(dt)

        time_delta = [stop_time]
        ball_result = ''
        for dt in time_delta:
            ball_result, _ = comp_evl.evolve(dt)

        # assert
        evl_result = []
        b_result = []
        for b in ball_result:
            if b.id == 0:
                b_result.append((b.pos[0], round(b.pos[1])))
        for evl in evolve_result:
            if evl.id == 0:
                evl_result.append((evl.pos[0], round(evl.pos[1])))
        self.assertEqual(evl_result, b_result)

    def test_ComputeTable_evolve_move2_stop_time(self):
        """
        Результат по прошествии очевидно слишком большого МНОГИХ значений времени и времени остановки должен быть одинаков
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (102, 100), (20, 90))

        comp_ball = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_ball.add_ball(0, 25, 0.100, (102, 100), (20, 90))
        stop_time = comp_ball.balls[0].stop_time
        # act
        time_delta = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        evolve_result = ''
        for dt in time_delta:
            evolve_result, _ = comp_evl.evolve(dt)

        time_delta = [stop_time]
        ball_result = ''
        for dt in time_delta:
            ball_result, _ = comp_evl.evolve(dt)

        # assert
        evl_result = []
        b_result = []
        for b in ball_result:
            if b.id == 0:
                b_result.append((b.pos[0], round(b.pos[1])))
        for evl in evolve_result:
            if evl.id == 0:
                evl_result.append((evl.pos[0], round(evl.pos[1])))
        self.assertEqual(evl_result, b_result)

    def test_ComputeTable_evolve_move4(self):
        """
        Вызов эволюции происходит много раз, хотя никакого движения нет. Позиция шара не должна изменится
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (102, 100), (0, 0))
        # act

        status = True
        time_delta = [1, 1, 1, 1, 1, 1]
        evolve_result = ''
        for dt in time_delta:
            evolve_result, status = comp_evl.evolve(dt)

        # assert
        evl_result = []

        for evl in evolve_result:
            if evl.id == 0:
                evl_result.append((evl.pos[0], round(evl.pos[1])))
        self.assertEqual((102, 100), evl_result[0])

    def test_ComputeTable_evolve_diagonal_move1(self):
        """
        Проверка диагонального движения по одному значению
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (100, 100), (150, 150))

        pre_calc = (669, 669)
        # act
        time_delta = [6]
        evolve_result = ''
        for dt in time_delta:
            evolve_result, _ = comp_evl.evolve(dt)

        # assert
        evl_result = []
        for evl in evolve_result:
            if evl.id == 0:
                evl_result.append((round(evl.pos[0]), round(evl.pos[1])))
        self.assertEqual(evl_result[0], pre_calc)

    def test_ComputeTable_evolve_diagonal_move2(self):
        """
        Проверка диагонального движения по одному значению
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (100, 100), (2, 150))

        pre_calc = (905, 905)
        # act
        time_delta = [300]
        evolve_result = ''
        for dt in time_delta:
            evolve_result, _ = comp_evl.evolve(dt)

        # assert
        evl_result = []
        for evl in evolve_result:
            if evl.id == 0:
                evl_result.append((round(evl.pos[0]), round(evl.pos[1])))
        self.assertEqual(pre_calc, evl_result)

    def test_ComputeTable_evolve_diagonal_move3(self):
        """
        Проверка диагонального движения по одному значению в отрицательную сторону
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (9000, 9000), (-150, -150))

        pre_calc = (905, 905)
        # act
        time_delta = [6]
        evolve_result = ''
        for dt in time_delta:
            evolve_result, _ = comp_evl.evolve(dt)

        # assert
        evl_result = []
        for evl in evolve_result:
            if evl.id == 0:
                evl_result.append((round(evl.pos[0]), round(evl.pos[1])))
        self.assertEqual(pre_calc, evl_result[0])

    def test_ComputeTable_evolve_diagonal_move4(self):
        """
        Проверка диагонального движения по одному значению в отрицательную сторону
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (9000, 9000), (150, -150))

        pre_calc = (905, 905)
        # act
        time_delta = [6, 6, 6, 6]
        evolve_result = ''
        for dt in time_delta:
            evolve_result, _ = comp_evl.evolve(dt)

        # assert
        evl_result = []
        for evl in evolve_result:
            if evl.id == 0:
                evl_result.append((round(evl.pos[0]), round(evl.pos[1])))
        self.assertEqual(pre_calc, evl_result[0])

    def test_ComputeTable_evolve_diagonal_move5(self):
        """
        Проверка диагонального движения по одному значению в отрицательную сторону
        """
        # arrange
        comp_evl = ComputeTable(topleft=(0, 0), bottomright=(10000, 10000))
        comp_evl.add_ball(0, 25, 0.100, (9000, 9000), (-150, 150))

        pre_calc = (905, 905)
        # act
        time_delta = [100]
        evolve_result = ''
        for dt in time_delta:
            evolve_result, _ = comp_evl.evolve(dt)

        # assert
        evl_result = []
        for evl in evolve_result:
            if evl.id == 0:
                evl_result.append((round(evl.pos[0]), round(evl.pos[1])))
        self.assertEqual(pre_calc, evl_result[0])
