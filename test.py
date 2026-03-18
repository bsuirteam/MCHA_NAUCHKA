import matplotlib.pyplot as plt
import numpy as np
import random as rnd



def turn_stretch(x, y, a, b, c, d, e):
    
    x_new = a*x + b
    y_new = c*x + d*y + e

    return x_new, y_new


def generate_fractal_IFS(params1,
                    params2,
                    iterations):

    x,y = 0.5, 0.2
    points_x=[]
    points_y=[]

    for i in range(iterations):

        if rnd.random() < 0.5:
            x,y = turn_stretch(x,y,*params1)
        else:
            x,y = turn_stretch(x,y,*params2)

        points_x.append(x)
        points_y.append(y)

    return points_x, points_y

def function(x):
    return 0.5 * (1 - 2*abs(x-0.5))
    # return np.sin(2 * np.pi * x)


def error(points_x, points_y, f):
    err = 0

    for x,y in zip(points_x,points_y):
        err += (y - f(x))**2

    return err / len(points_x)

c_range = (-2, 2)
d_range = (-0.5, 0.5)
e_range = (-1, 1)

mutation_range = [
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
]


def random_params():

    a1 = 0.5
    a2 = 0.5

    b1 = 0
    b2 = 0.5

    c1 = rnd.uniform(*c_range)
    c2 = rnd.uniform(*c_range)

    d1 = rnd.uniform(*d_range)
    d2 = rnd.uniform(*d_range)

    e1 = rnd.uniform(*e_range)
    e2 = rnd.uniform(*e_range)

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

def random_population(size):
    return [random_params() for _ in range(size)]

def cross_over(params1, params2):
    return tuple(x[rnd.randint(0, 1)] for x in (zip(params1, params2)))

def mutant(params):
    return tuple(params[i] + rnd.uniform(*mutation_range[i]) for i in range(len(params)))


def evolution():
    N = 5000
    population_size = 100
    generations = 100
    best_params = 0
    best_error = float("inf")

    population = random_population(population_size)

    for _ in range(generations):
        scores = []

        for params in population:
            px, py = generate_fractal_IFS(params[:5], params[5:], N)
            e = error(px, py, function)
            scores.append((e, params))

        scores.sort()

        if (scores[0][0] < best_error):
            best_params = scores[0][1]
            best_error = scores[0][0]

        best = [p for _,p in scores[:20]]

        new_population = best.copy()

        while len(new_population) < population_size:

            p1,p2 = rnd.sample(best,2)

            child = cross_over(p1,p2)

            child = mutant(child)

            new_population.append(child)

        population = new_population

        print(best_error)

    return best_params

best_params = evolution()

print(best_params)

points_x, points_y = generate_fractal_IFS(best_params[:5], best_params[5:], 900000)

print(error(points_x, points_y, function))

plt.figure(figsize=(6,6))
plt.scatter(points_x, points_y, s=1, linewidths=0.1, c="red")

x = np.linspace(0, 1, 500)
y = function(x)

plt.plot(x, y, c="blue")

plt.gca().set_aspect('equal')
plt.show()