import matplotlib.pyplot as plt
import numpy as np
import random as rnd
from multiprocessing import Pool, cpu_count
from numba import njit
import pandas as pd


# a - Сжатие по x
# b - Смещение по x
# c - Наклон (поворот)
# d - Сжатие по y + степень фрактальности
# e - Смещение по y
#@njit
def affine_transformation(x: float, y: float, a: float, b: float, c: float, d: float, e: float) -> tuple[float, float]:
    
    x_new = a * x + b
    y_new = c * x + d * y + e

    return x_new, y_new

#@njit
def generate_fractal_IFS_fast(ifs_array,x_start, y_start, iterations, probs):
    
    res = np.empty((iterations, 2), dtype=np.float64)

    px = np.empty(iterations, dtype=np.float64)
    py = np.empty(iterations, dtype=np.float64)
    

    cdf = np.cumsum(probs)
    
    x, y = x_start, y_start
    
    for i in range(iterations):
        r = np.random.random()
        idx = 0
        for j in range(len(cdf)):
            if r < cdf[j]:
                idx = j
                break
    
        a = ifs_array[idx, 0]
        b = ifs_array[idx, 1]
        c = ifs_array[idx, 2]
        d = ifs_array[idx, 3]
        e = ifs_array[idx, 4]

        # Сама трансформация
        x_new = a * x + b 
        y_new = c * x + d * y + e
        
        x, y = x_new, y_new
        
        res[i, 0] = x
        res[i, 1] = y

        px[i] = x
        py[i] = y

    return px, py

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


# Интерполируемое множество точек
# X_data = np.sort(np.concatenate(([0.0], np.random.rand(10), [1.0])))
# Y_data = 0.5 * (1 - 2*abs( X_data - 0.5)) + np.random.normal(0, 0.05, len(X_data))
# Y_data = np.sin(2 * np.pi * X_data) + np.random.normal(-0.1, 0.1, len(X_data))

X_data = np.sort(np.concatenate(([0.0], np.random.uniform(0, 1, 4), [1.0])))
Y_data = 0.5 * (1 - 2*abs( X_data - 0.5)) + np.random.normal(0, 0.1, len(X_data))

Errors_data = []

# Среднеквадратическое отклонение
def error_for_data(points_x : tuple,
        points_y : tuple, 
        X_data : tuple,
        Y_data : tuple) -> float:
    err = 0
    count = 0
    
    for x, y in zip(points_x, points_y):
        # if x < 0 or x > 1:
        #     err += 100.0
        #     continue
            
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


def error_for_data_fast(points_x, points_y, X_data, Y_data):
    px = np.asarray(points_x)
    py = np.asarray(points_y)
    # Фильтруем точки вне [0, 1]
    mask = (px >= 0) & (px <= 1)
    if mask.sum() == 0:
        return 500.0
    px, py = px[mask], py[mask]
    
    # Векторный searchsorted вместо цикла
    i = np.searchsorted(X_data, px) - 1
    i = np.clip(i, 0, len(X_data) - 2)
    
    x1, y1 = X_data[i], Y_data[i]
    x2, y2 = X_data[i+1], Y_data[i+1]
    
    t = (px - x1) / (x2 - x1)
    y_interp = y1 + t * (y2 - y1)
    
    return float(np.mean((py - y_interp) ** 2))



# Генерация случайных коэффициентов для y
def random_params(x_i : float,
                x_i1 : float,
                c_range : tuple[float, float],
                d : float,
                e_range : tuple[float, float]) -> tuple:
    a = x_i1 - x_i

    b = x_i

    c = rnd.uniform(*c_range)

    e = rnd.uniform(*e_range)

    # Условие сжимаемости
    if ((np.fabs(a * d) >= 1)):
        return random_params(x_i, x_i1, c_range, d, e_range)    

    return (
        a, b, c, d, e
    )

def random_IFS(X_data : tuple,
                c_range : tuple[float, float],
                d : float,
                e_range : tuple[float, float]) -> tuple:
    
    return tuple(random_params(X_data[i], X_data[i + 1], c_range, d, e_range) for i in range(len(X_data)- 1))

# Генерация случайно популяции
def random_population(size : int, 
                    X_data : tuple,
                    c_range : tuple[float, float],
                    d : float,
                    e_range : tuple[float, float]) -> tuple:
    return tuple(random_IFS(X_data, c_range, d, e_range) for _ in range(size))

# Перемешивание
def cross_over(IFS1 : tuple, IFS2 : tuple, alpha : float = 0.3) -> tuple:
    child = []
    
    # Итерируемся по строкам (матрицам) фрактала
    for m1, m2 in zip(IFS1, IFS2):
        # 1. Выбираем базовую матрицу-донора (случайно 50/50)
        base = m1 if rnd.random() < 0.5 else m2
        target = m2 if base is m1 else m1
        
        # 2. Применяем BLX-alpha интерполяцию для каждого коэффициента в матрице
        new_matrix = []
        for p_base, p_target in zip(base, target):
            d = abs(p_base - p_target)
            # Генерируем значение в расширенном интервале между родителями
            val = rnd.uniform(min(p_base, p_target) - alpha * d, 
                              max(p_base, p_target) + alpha * d)
            new_matrix.append(val)
            
        child.append(tuple(new_matrix))
        
    return tuple(child)

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


def tournament_select(scored_population: list, k: int = 3) -> tuple:
    """Турнирная селекция: выбирает лучшего из k случайных."""
    contestants = rnd.sample(scored_population, k)
    return min(contestants, key=lambda x: x[0])[1]

def evaluate_ifs(args):
    IFS, x_start, y_start, fractal_depth_evolution = args
    

    ifs_data = np.ascontiguousarray(np.array(IFS))

        # Считаем веса (можно по твоей логике или по определителю)
    # Обычно вероятность пропорциональна площади: abs(a*d - b*c)
    weights = ifs_data[:, 0] # Твоя логика: первый коэффициент
    probs = weights / np.sum(weights)

    px, py = generate_fractal_IFS_fast(
        ifs_data,
        x_start,
        y_start,
        fractal_depth_evolution,
        probs
    )

    e = error_for_data_fast(px, py, X_data, Y_data)
    
    return (e, IFS)

# Генетический метод
def evolution(population_size : int, generations : int, survived_population : int, mutation_range : tuple) -> tuple:
    global x_start, y_start, a1, a2, b1, b2, c_range, d, e_range, fractal_depth_evolution, function, X_data, Y_data, waiting_for_mutation, Errors_data

    best_params = 0
    best_error = float("inf")
    current_waiting = 0
    saved_mut = mutation_range

    population = random_population(population_size, X_data, c_range, d, e_range)

    for i in range(generations):
        scores = []

        args_list = [
            (IFS, x_start, y_start, fractal_depth_evolution)
            for IFS in population
        ]

        with Pool(cpu_count()) as pool:
            scores = pool.map(evaluate_ifs, args_list, chunksize=1000)

        scores.sort()

        if (scores[0][0] < best_error):
            best_params = scores[0][1]
            best_error = scores[0][0]
            mutation_range = saved_mut

        elif (scores[0][0] >= best_error):
            current_waiting+=1
            if (current_waiting == waiting_for_mutation):
                mutation_range *= 5
                current_waiting = 0
                print("Mutated")
            

        best = [p for _,p in scores[:survived_population]]

        new_population = best.copy()

        while len(new_population) < population_size:

            p1 = tournament_select(scores)

            p2 = tournament_select(scores)

            child = cross_over(p1,p2)

            child = mutant(child, mutation_range)

            new_population.append(child)

        population = new_population

        print(best_error)
        Errors_data.append([i + 1, best_error])

    return best_params


# Начальная точка для IFS
x_start = 0.5
y_start = 0.3

# Границы для генерации коэффициентов
c_range = (0.3, 0.7)
d = 0.15
e_range = (-0.5, 0.5)

# Глубина фрактала
fractal_depth_evolution = 1000
fractal_depth_graph = 1000

# Параметры генетического метода
population_size = 100
generations = 50   
survived_population = 3
mutation_range = (
    (0,0),      
    (0,0),      
    (-0.1, 0.1), 
    (0, 0), 
    (-0.05, 0.05), 
)
waiting_for_mutation = 3

if __name__ == "__main__":
    # Результат интерполяции (коэффициенты)
    best_IFS = evolution(population_size, generations, survived_population, mutation_range)
    print(best_IFS)

    ifs_data = np.ascontiguousarray(np.array(best_IFS))
    weights = ifs_data[:, 0]
    probs = weights / np.sum(weights)

    # Результат интерполяции (ошибка)
    points_x, points_y = generate_fractal_IFS_fast(ifs_data,
                                            x_start,
                                            y_start,
                                            fractal_depth_graph,
                                            probs)
    print(error_for_data(points_x, points_y, X_data, Y_data))

    df = pd.DataFrame(Errors_data, columns=["Generation", "Error"])
    df.to_csv("errors.csv", index=False)

    # Графическое отображение фрактала
    plt.figure(figsize=(6,6))
    plt.scatter(points_x, points_y, s=1, linewidths=0.1, c="red")

    plt.plot(X_data, Y_data, c="blue")

    plt.gca().set_aspect('equal')
    plt.show()