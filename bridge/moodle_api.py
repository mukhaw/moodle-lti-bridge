import logging

import requests

logger = logging.getLogger(__name__)


def get_best_grade(api_url, token, user_id, quiz_id):
    function = 'mod_quiz_get_user_best_grade'
    data = {
        'userid': user_id,
        'quizid': quiz_id
    }
    response = moodle_function(api_url, token, function, data)
    if response['hasgrade']:
        return response['grade']
    else:
        return -1


def get_user_attempts(api_url, token, user_id, quiz_id):
    function = 'mod_quiz_get_user_attempts'
    data = {
        'userid': user_id,
        'quizid': quiz_id,
        'status': 'all'
    }
    return moodle_function(api_url, token, function, data)


def get_quizzes_by_courses(api_url, token, course_id):
    function = 'mod_quiz_get_quizzes_by_courses'
    data = {
        'courseids[0]': course_id
    }
    return moodle_function(api_url, token, function, data)


def get_user(api_url, token, email):
    function = 'core_user_get_users'
    # function = 'core_search_get_relevant_users'
    data = {
        'criteria[0][key]': 'email',
        'criteria[0][value]': email
    }
    users = moodle_function(api_url, token, function, data)['users']
    if not users:
        return None
    return users[0]


def moodle_function(api_url, token, function, data):
    logger.info(data)
    logger.info(api_url)
    return requests.post(api_url.format(token, function), data=data).json()
