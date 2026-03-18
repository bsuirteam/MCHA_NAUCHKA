import matplotlib.pyplot as plt
import numpy as np
import random as rnd


# a - Сжатие по x
# b - Смещение по x
# c - Наклон (поворот)
# d - Сжатие по y + степень фрактальности
# e - Смещение по y
def affine_transformation(x: float, y: float, a: float, b: float, c: float, d: float, e: float) -> tuple[float, float]:
    
    x_new = a * x + b
    y_new = c * x + d * y + e

    return x_new, y_new

# IFS фрактал
def generate_fractal_IFS(params1 : tuple,
                    params2 : tuple,
                    x_start : float,
                    y_start : float,
                    iterations : int) -> tuple[float, float]:

    x,y = x_start, y_start
    points_x=[]
    points_y=[]

    for _ in range(iterations):

        if rnd.random() < 0.5:
            x,y = affine_transformation(x,y,*params1)
        else:
            x,y = affine_transformation(x,y,*params2)

        points_x.append(x)
        points_y.append(y)

    return points_x, points_y

# Интерполируемая функция
def function(x: float) -> float:
    return 0.5 * (1 - 2*abs(x-0.5))
    # return np.sin(2 * np.pi * x)

# Интерполируемое множество точек
X_data = np.sort(np.random.rand(50))
Y_data = 0.5 * (1 - 2*abs( X_data - 0.5)) + np.random.normal(0, 0.1, len(X_data))

# Среднеквадратическое отклонение
def error(points_x : tuple,
        points_y : tuple, 
        f) -> float:
    err = 0

    for x,y in zip(points_x,points_y):
        err += (y - f(x))**2

    return err / len(points_x)

def error_for_data(points_x : tuple,
        points_y : tuple, 
        X_data : tuple,
        Y_data : tuple) -> float:
    err = 0

    for x,y in zip(points_x,points_y):
        
        i = np.argmin(np.abs(X_data - x))
        dx = X_data[i] - x
        dy = Y_data[i] - y

        err += dx**2 + dy**2

    return err / len(points_x)



# Генерация случайных коэффициентов для y
def random_params(a1 : float,
                a2 : float,
                b1: float,
                b2 : float,
                c_range : tuple[float, float],
                d_range : tuple[float, float],
                e_range : tuple[float, float]) -> tuple:

    c1 = rnd.uniform(*c_range)
    c2 = rnd.uniform(*c_range)

    d1 = rnd.uniform(*d_range)
    d2 = rnd.uniform(*d_range)

    e1 = rnd.uniform(*e_range)
    e2 = rnd.uniform(*e_range)

    # Условие сжимаемости
    if ((np.fabs(a1 * d1) >= 1) or (np.fabs(a2 * d2) >= 1)):
        return random_params()    

    return (
        a1, 
        b1,
        c1,
        d1,
        e1,

        a2, 
        b2,
        c2,
        d2,
        e2,
    )

# Генерация случайно популяции
def random_population(size : int, 
                    a1 : float,
                    a2 : float,
                    b1: float,
                    b2 : float,
                    c_range : tuple[float, float],
                    d_range : tuple[float, float],
                    e_range : tuple[float, float]) -> tuple:
    return tuple(random_params(a1, a2, b1, b2, c_range, d_range, e_range) for _ in range(size))

# Перемешивание
def cross_over(params1 : tuple, params2 : tuple) -> tuple:
    return tuple(x[rnd.randint(0, 1)] for x in (zip(params1, params2)))

# Мутации
def mutant(params : tuple, mutation_range : tuple) -> tuple:
    return tuple(params[i] + rnd.uniform(*mutation_range[i]) for i in range(len(params)))

# Генетический метод
def evolution(population_size : int, generations : int, survived_population : int, mutation_range : tuple) -> tuple:
    global x_start, y_start, a1, a2, b1, b2, c_range, d_range, e_range, fractal_depth_evolution, function, X_data, Y_data

    best_params = 0
    best_error = float("inf")

    population = random_population(population_size, a1, a2, b1, b2, c_range, d_range, e_range)

    for _ in range(generations):
        scores = []

        for params in population:
            px, py = generate_fractal_IFS(params[:len(params) // 2], 
                                        params[len(params) // 2:], 
                                        x_start,
                                        y_start,
                                        fractal_depth_evolution)
            # e = error(px, py, function)
            e = error_for_data(px, py, X_data, Y_data)
            scores.append((e, params))

        scores.sort()

        if (scores[0][0] < best_error):
            best_params = scores[0][1]
            best_error = scores[0][0]

        best = [p for _,p in scores[:survived_population]]

        new_population = best.copy()

        while len(new_population) < population_size:

            p1,p2 = rnd.sample(best,2)

            child = cross_over(p1,p2)

            child = mutant(child, mutation_range)

            new_population.append(child)

        population = new_population

        print(best_error)

    return best_params

# Начальная точка для IFS
x_start = 0.5
y_start = 0.3

# Постоянные коэффициенты
a1 = 0.5
a2 = 0.5
b1 = 0
b2 = 0.5

# Границы для генерации коэффициентов
c_range = (-2, 2)
d_range = (-0.5, 0.5)
e_range = (-1, 1)


# Глубина фрактала
fractal_depth_evolution = 5000
fractal_depth_graph = 10000

# Параметры генетического метода
population_size = 100
generations = 100
survived_population = 20
mutation_range = (
    (-0,0),
    (-0,0),
    (-0.05, 0.05),
    (-0.05, 0.05),
    (-0.05, 0.05),

    (-0,0),
    (-0,0),
    (-0.05, 0.05),
    (-0.05, 0.05),
    (-0.05, 0.05),
)

# Результат интерполяции (коэффициенты)
best_params = (0.5, 0.0, 0.42693793237700967, 0.08987851368160676, 0.03635309280920177, 0.5, 0.5, -0.45572009683533815, 0.06069548502594522, 0.45825248071831315)
print(best_params)

# Результат интерполяции (ошибка)
points_x, points_y = generate_fractal_IFS(best_params[:len(best_params) // 2], 
                                        best_params[len(best_params) // 2:],
                                        x_start,
                                        y_start,
                                        fractal_depth_graph)
print(error_for_data(points_x, points_y, X_data, Y_data))

# Графическое отображение фрактала
plt.figure(figsize=(6,6))
plt.scatter(points_x, points_y, s=1, linewidths=0.1, c="red")

# Графическое отображение исходной функции
# x = np.linspace(0, 1, 500)
# y = function(x)
# plt.plot(x, y, c="blue")
plt.plot(X_data, Y_data, c="blue")

plt.gca().set_aspect('equal')
plt.show()