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
