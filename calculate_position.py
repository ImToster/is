from flags import FLAGS
import math


def solve_system(x1, y1, x2, y2, x3, y3, d1, d2, d3):
    solutions = []
    if x1 == x2:
        y = (y2**2 - y1**2 + d1**2 - d2**2) / (2 * (y2 - y1))
        x = x1 + math.sqrt(d1**2 - (y - y1)**2)
        if abs(x) <= 57.5:
            solutions.append((x, y))
        x = x1 - math.sqrt(d1**2 - (y - y1)**2)
        if abs(x) <= 57.5:
            solutions.append((x, y))
    else:
        alpha = (y1 - y2) / (x2 - x1)
        beta = (y2**2 - y1**2 + x2**2 - x1**2 +
                d1**2 - d2**2) / (2 * (x2 - x1))

        a = alpha**2 + 1
        b = -2 * (alpha * (x1 - beta) + y1)
        c = (x1 - beta) ** 2 + y1 ** 2 - d1 ** 2

        if (b**2 - 4*a*c < 0):
            return None
        y = (-b + math.sqrt(b**2 - 4*a*c)) / (2 * a)
        x = alpha * y + beta
        if abs(y) <= 39:
            solutions.append((x, y))
        y = (-b - math.sqrt(b**2 - 4*a*c)) / (2 * a)
        x = alpha * y + beta
        if abs(y) <= 39:
            solutions.append((x, y))
    if len(solutions) == 1:
        return solutions[0]
    s1_x, s1_y = solutions[0]
    s2_x, s2_y = solutions[1]
    if (abs((s1_x - x3)**2 + (s1_y - y3)**2 - d3**2) < abs((s2_x - x3)**2 + (s2_y - y3)**2 - d3**2)):
        return s1_x, s1_y
    else:
        return s2_x, s2_y


def calculate_agent_position(visible_flags):
    if len(visible_flags) < 3:
        return None
    f1, f2, f3 = visible_flags[0], visible_flags[1], visible_flags[2]
    x1, y1 = FLAGS["".join(f1["name"])]
    d1 = f1["distance"]
    x2, y2 = FLAGS["".join(f2["name"])]
    d2 = f2["distance"]
    x3, y3 = FLAGS["".join(f3["name"])]
    d3 = f3["distance"]
    pos = solve_system(x1, y1, x2, y2, x3, y3, d1, d2, d3)

    while not pos:
        if d1 < d2:
            d1 += 0.1
        else:
            d2 += 0.1
        pos = solve_system(x1, y1, x2, y2, x3, y3, d1, d2, d3)
    return pos


def calculate_object_position(agent_pos, object, visible_flags):
    if len(visible_flags) < 2:
        return None
    f1, f2 = visible_flags[0], visible_flags[1]

    x1, y1 = FLAGS["".join(f1["name"])]
    alpha1 = f1["direction"]
    d1 = f1["distance"]

    x2, y2 = FLAGS["".join(f2["name"])]
    alpha2 = f2["direction"]
    d2 = f2["distance"]

    x, y = agent_pos
    d_a = object["distance"]
    alpha_a = object["direction"]

    d_a1 = math.sqrt(d1**2 + d_a**2 - 2 * d1 * d_a *
                     math.cos(math.radians(alpha1 - alpha_a)))
    d_a2 = math.sqrt(d2**2 + d_a**2 - 2 * d2 * d_a *
                     math.cos(math.radians(alpha2 - alpha_a)))

    object_pos = solve_system(x, y, x1, y1, x2, y2, d_a, d_a1, d_a2)

    while not object_pos:
        if d_a < d_a1:
            d_a += 0.1
        else:
            d_a1 += 0.1
        object_pos = solve_system(x, y, x1, y1, x2, y2, d_a, d_a1, d_a2)
    return object_pos
