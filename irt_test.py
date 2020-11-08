import matplotlib.pyplot as plt
import numpy as np


# none 0
# very low .01 - .34
# Low .35 - .64
# moderate .65 - 1.34
# High 1.35 - 1.69
# Very high > 1.70
# Perfect + infinity

def P_two(thi, a, b):
    return np.exp(a * (thi - b)) / (1 + np.exp(a * (thi - b)))


def I_two(thi, x):
    p = P_two(thi, x['a'], x['b'])
    return x['a'] ** 2 * p * (1 - p)


def P_one(thi, b):
    return 1 / (1 + np.exp(-1 * (thi - b)))


def I_one(thi, x):
    p = P_one(thi, x['b'])
    return p * (1 - p)


def square_error(answers):
    denominator = 0
    for x in answers:
        denominator = denominator + I_two(thi, x)
    return 1 / (denominator ** 0.5)


def thi_next(thi, answers):
    numerator = 0
    denominator = 0
    for x in answers:
        p = P_two(thi, x['a'], x['b'])
        numerator = numerator + x['a'] * (x['ans'] - p)
        denominator = denominator + I_two(thi, x)

    return thi + numerator / denominator


def choose_item(thi, items):
    I_max = -100
    for item in items:
        I_cur = I_two(thi, item)
        if I_cur > I_max:
            chosen_item = item
            I_max = I_cur
    return chosen_item


items = [
    {'a': 1.7, 'b': 0.1, 'ans': 1},
    {'a': 1.7, 'b': 0.25, 'ans': 0},
    {'a': 1.7, 'b': 0.7, 'ans': 1},
    {'a': 1.7, 'b': 1.2, 'ans': 0},
    {'a': 1.7, 'b': 1.5, 'ans': 1},
    {'a': 1.7, 'b': 1.8, 'ans': 1},
    {'a': 1.7, 'b': 1.9, 'ans': 1},
    {'a': 1.7, 'b': 2.1, 'ans': 0},
    {'a': 1.7, 'b': 2.4, 'ans': 1},
    {'a': 1.7, 'b': 2.5, 'ans': 0},
]

thi = 0.5
error = 100

answers = []
x_axis = np.linspace(-10, 10, 100)

idx = 0

while thi < 1.4 or error > 0.9:
    i = choose_item(thi, items)
    print('chosen item ' + str(i))
    plt.plot(x_axis, I_two(x_axis, i), label='2PL_I')
    plt.plot(x_axis, P_two(x_axis, i['a'], i['b']), label='2PL')
    # plt.plot(x_axis, P_one(x_axis, i['b']), label='Rasch')
    # plt.plot(x_axis, I_one(x_axis, i), label='Rasch_I')
    answers.append(i)
    thi = thi_next(thi, answers)
    print('thi: ' + str(thi))
    plt.text(thi, 0.8, 'thi_' + str(idx))
    plt.axvline(x=thi, label='thi_' + str(idx) + '_' + str(thi))
    error = square_error(answers)
    print('error: ' + str(error))
    idx = idx + 1

plt.xlabel('x')
plt.xlim([-3, 3])
plt.ylabel('P(thi)')
plt.title('The logistic function', fontsize=15)
plt.show()
