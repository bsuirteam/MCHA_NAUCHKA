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
def generate_fractal_IFS(IFS : tuple,
                    x_start : float,
                    y_start : float,
                    iterations : int) -> tuple[float, float]:

    x,y = x_start, y_start
    points_x=[]
    points_y=[]

    interval_lengths = [IFS[i][0] for i in range(len(IFS))]
    total_length = sum(interval_lengths)
    probabilities = [length / total_length for length in interval_lengths]
    
    for _ in range(iterations):
        idx = np.random.choice(len(IFS), p=probabilities)
        x, y = affine_transformation(x, y, *IFS[idx])

        points_x.append(x)
        points_y.append(y)

    return points_x, points_y

def collage_theorem(IFS : tuple,
                    X_data : tuple,
                    Y_data : tuple):
    points_x=[]
    points_y=[]

    interval_lengths = [IFS[i][0] for i in range(len(IFS))]
    total_length = sum(interval_lengths)
    probabilities = [length / total_length for length in interval_lengths]
    
    for i in range(len(X_data)):
        j = 0

        if i > 0:
            j = i - 1

        x, y = affine_transformation(X_data[i], Y_data[i], *IFS[j])

        points_x.append(x)
        points_y.append(y)

    return points_x, points_y

# Интерполируемая функция
def function(x: float) -> float:
    return 0.5 * (1 - 2*abs(x-0.5))

# Интерполируемое множество точек
X_data = np.sort(np.concatenate(([0.0], np.random.rand(2), [1.0])))
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
    count = 0
    
    for x, y in zip(points_x, points_y):
        if x < 0 or x > 1:
            err += 100.0
            continue
            
        # Линейная интерполяция между ближайшими точками
        i = np.searchsorted(X_data, x) - 1
        if i < 0: i = 0
        if i >= len(X_data)-1: i = len(X_data)-2
            
        x1, y1 = X_data[i], Y_data[i]
        x2, y2 = X_data[i+1], Y_data[i+1]
        
        # Линейная интерполяция
        t = (x - x1) / (x2 - x1)
        y_interp = y1 + t * (y2 - y1)
        
        err += (y - y_interp)**2
        count += 1
    
    return err / max(count, 1)

def error_collage(points_x : tuple,
        points_y : tuple, 
        X_data : tuple,
        Y_data : tuple) -> float:
    err = 0
    count = 0
    
    for i in range(len(Y_data)):
        err += (Y_data[i] - points_y[i])**2
        count += 1
    
    return err / max(count, 1)


# Генерация случайных коэффициентов для y
def random_params(x_i : float,
                x_i1 : float,
                c_range : tuple[float, float],
                d_range : tuple[float, float],
                e_range : tuple[float, float]) -> tuple:
    a = x_i1 - x_i

    b = x_i

    c = rnd.uniform(*c_range)

    d = rnd.uniform(*d_range)

    e = rnd.uniform(*e_range)
    # Условие сжимаемости
    if ((np.fabs(a * d) >= 1)):
        return random_params(x_i, x_i1, c_range, d_range, e_range)    

    return (
        a, b, c, d, e
    )

def random_IFS(X_data : tuple,
                c_range : tuple[float, float],
                d_range : tuple[float, float],
                e_range : tuple[float, float]) -> tuple:
    
    return tuple(random_params(X_data[i], X_data[i + 1], c_range, d_range, e_range) for i in range(len(X_data)- 1))

# Генерация случайно популяции
def random_population(size : int, 
                    X_data : tuple,
                    c_range : tuple[float, float],
                    d_range : tuple[float, float],
                    e_range : tuple[float, float]) -> tuple:
    return tuple(random_IFS(X_data, c_range, d_range, e_range) for _ in range(size))

# Перемешивание
def cross_over(IFS1 : tuple, IFS2 : tuple) -> tuple:
    return tuple(x[rnd.randint(0, 1)] for x in (zip(IFS1, IFS2)))

# Мутации
def mutant(IFS : tuple, mutation_range : tuple) -> tuple:
    mutated = []
    for params in IFS:
        new_params = tuple(
            params[i] + rnd.uniform(*mutation_range[i]) 
            for i in range(len(params))
        )
        mutated.append(new_params)
    return tuple(mutated)

# Генетический метод
def evolution(population_size : int, generations : int, survived_population : int, mutation_range : tuple) -> tuple:
    global x_start, y_start, a1, a2, b1, b2, c_range, d_range, e_range, fractal_depth_evolution, function, X_data, Y_data

    best_params = 0
    best_error = float("inf")

    population = random_population(population_size, X_data, c_range, d_range, e_range)

    for _ in range(generations):
        scores = []

        for IFS in population:
            px, py = generate_fractal_IFS(IFS, 
                                        x_start,
                                        y_start,
                                        fractal_depth_evolution)

            # px, py = collage_theorem(IFS, X_data, Y_data)

            # e = error(px, py, function)
            e = error_for_data(px, py, X_data, Y_data)
            # e = error_collage(px, py, X_data, Y_data)
            scores.append((e, IFS))

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

def evolution_collage(population_size : int, generations : int, survived_population : int, mutation_range : tuple) -> tuple:
    global x_start, y_start, a1, a2, b1, b2, c_range, d_range, e_range, fractal_depth_evolution, function, X_data, Y_data

    best_params = 0
    best_error = float("inf")

    population = random_population(population_size, X_data, c_range, d_range, e_range)

    for _ in range(generations):
        scores = []

        for IFS in population:
            # px, py = generate_fractal_IFS(IFS, 
            #                             x_start,
            #                             y_start,
            #                             fractal_depth_evolution)

            px, py = collage_theorem(IFS, X_data, Y_data)

            # e = error(px, py, function)
            # e = error_for_data(px, py, X_data, Y_data)
            e = error_collage(px, py, X_data, Y_data)
            scores.append((e, IFS))

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
d_range = (-0.15, 0.15)
e_range = (-1, 1)


# Глубина фрактала
fractal_depth_evolution = 1000  # больше точек для оценки
fractal_depth_graph = 15000      # для красивого графика

# Параметры генетического метода
population_size = 100
generations = 1000             # ДЛЯ КОЛЛАЖА МОЖЕШЬ СМЕЛО БРАТЬ 5000 И БОЛЬШЕ А БЕЗ ОКОЛО 50   
survived_population = 20
mutation_range = (
    (0,0),      
    (0,0),      
    (-0.1, 0.1), 
    (-0.01, 0.01), 
    (-0.05, 0.05), 
)
# Результат интерполяции (коэффициенты)
best_IFS = evolution_collage(population_size, generations, survived_population, mutation_range)
print(best_IFS)

# Результат интерполяции (ошибка)
points_x, points_y = generate_fractal_IFS(best_IFS,
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