import numpy as np

from adaptive_engine.engine.IEngine import IEngine
from bridge import models
from bridge.constants import *


class IRTEngine(IEngine):

    def select_activity(self, activities, **params):
        if not activities:
            return None

        user_data = params['user_data']
        target_descriptor = models.find_target_descriptor(user_data[TITLE])

        if not target_descriptor:
            return None

        target_descriptor = target_descriptor[0]

        user = models.get_user(user_data[EMAIL])

        thi = get_thi(target_descriptor, user)

        activities = list(filter(lambda x: x in target_descriptor.tasks, activities))

        I_max = -100
        most_satisfied_item = None
        for item in activities:
            task = {
                'a': item.sub_descriptor.get(target_descriptor, 'a'),
                'b': item.sub_descriptor.get(target_descriptor, 'b')
            }
            I_cur = I(thi, task)
            if I_cur > I_max:
                most_satisfied_item = item
                I_max = I_cur
        return most_satisfied_item

    def commit_result(self, user, task, grade):
        if not grade > 0:
            return user

        if grade > 1:
            grade = 1

        user.did.add(task, properties={'grade': grade})

        for sd in task.sub_descriptor:
            task_answer = {
                              'a': task.sub_descriptor.get(sd, 'a'),
                              'b': task.sub_descriptor.get(sd, 'b'),
                              'ans': grade
                          }

            thi = get_thi(sd, user)

            numerator = get_numerator(sd, user)

            denominator = get_denominator(sd, user)

            new_thi, new_numerator, new_denominator = thi_next(thi, numerator, denominator, task_answer)

            user.knows.update(sd, properties={
                THI: new_thi,
                NUMERATOR: new_numerator,
                DENOMINATOR: new_denominator,
                ERROR: square_error(new_denominator)
            })

        return user


def P(thi, a, b):
    return np.exp(a * (thi - b)) / (1 + np.exp(a * (thi - b)))


def I(thi, x):
    p = P(thi, x['a'], x['b'])
    return x['a'] ** 2 * p * (1 - p)


def thi_next(thi, numerator, denominator, task_answer):
    p = P(thi, task_answer['a'], task_answer['b'])
    numerator = numerator + task_answer['a'] * (task_answer['ans'] - p)
    denominator = denominator + I(thi, task_answer)

    return thi + numerator / denominator, numerator, denominator


def square_error(denominator):
    return 1 / (denominator ** 0.5)


def get_thi(target_descriptor, user):
    thi = user.knows.get(target_descriptor, THI)
    if not thi:
        thi = APRIOR_THI
    return thi


def get_denominator(target_descriptor, user):
    denominator = user.knows.get(target_descriptor, DENOMINATOR)
    if not denominator:
        denominator = 0
    return denominator


def get_numerator(target_descriptor, user):
    numerator = user.knows.get(target_descriptor, NUMERATOR)
    if not numerator:
        numerator = 0
    return numerator
