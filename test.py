import matplotlib.pyplot as plt
import numpy as np

def L(x, y, a, b, c, d, e):
    x_new = a*x + b
    y_new = c*x + d*y + e
    return x_new, y_new

def R(x, y, a, b, c, d, e):
    x_new = a*x + b
    y_new = c*x + d*y + e
    return x_new, y_new


# print("Введите параметры преобразования a b c d:")
# a, b, c, d = map(float, input().split())

# P = int(input("Введите глубину фрактала P: "))

def generate_fractal(a_1, b_1, c_1, d_1, e_1, a_2, b_2, c_2, d_2, e_2, P):

    x1 = [0]*(P+1)
    y1 = [0]*(P+1)
    x2 = [0]*(P+1)
    y2 = [0]*(P+1)

    # x1[0] = a_1
    # y1[0] = b_1

    points_x = [0, 1]
    points_y = [0, 0]


    def step(S):
        x1[S-1] = x2[S-1]
        y1[S-1] = y2[S-1]

        for j in range(S, P+1):
            x = x1[j-1]
            y = y1[j-1]

            x1[j], y1[j] = L(x, y, a_1, b_1, c_1, d_1, e_1)

            x2[j], y2[j] = R(x, y, a_2, b_2, c_2, d_2, e_2)

            points_x.append(x1[j])
            points_y.append(y1[j])

            points_x.append(x2[j])
            points_y.append(y2[j])


    S = 1
    step(S)

    for m in range(1, 2**(P-1)):
        S = P
        n = m

        while n % 2 == 0:
            n //= 2
            S -= 1

        step(S)

    return points_x, points_y

# def function(x):
#     return np.sin(x)

# def error(points, f):
#     err = 0
#     for x,y in points:
#         err += (y - f(x))**2
#     return err/len(points)

# best = float('inf')
# for a in np.linspace(0.4,0.7,20):
#     for b in np.linspace(-0.7,0.7,20):
#         for c in np.linspace(0.4,0.7,20):
#             for d in np.linspace(-0.7,0.7,20):

#                 points = generate_fractal(a,b,c,d,P=8)

#                 e = error(points,function)

#                 if e < best:
#                     best = e
#                     best_params = (a,b,c,d)

# print(best_params,best)

def generate_fractal_IFS(a1,b1,c1,d1,e1,
                     a2,b2,c2,d2,e2,
                     iterations):

    x,y = 0,0
    points_x=[]
    points_y=[]

    import random

    for _ in range(iterations):

        if random.random()<0.5:
            x,y = L(x,y,a1,b1,c1,d1,e1)
        else:
            x,y = L(x,y,a2,b2,c2,d2,e2)

        points_x.append(x)
        points_y.append(y)

    return points_x,points_y


points_x, points_y = points = generate_fractal(
    0.5, 0, 0.8, 0.3, 0,
    0.5, 0.5, -0.8, 0.3, 0.5,
    15
)

plt.figure(figsize=(6,6))
plt.scatter(points_x, points_y, s=1, linewidths=0.1, antialiased=False)

x = np.linspace(0, 1, 500)
y = np.sin(2*np.pi*x)

plt.plot(x, y)

plt.gca().set_aspect('equal')
plt.show()