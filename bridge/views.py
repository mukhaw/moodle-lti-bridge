import logging
import uuid
from urllib.parse import urlparse
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lti import ToolConsumer

from bridge import moodle_api, models, engine
from bridge.constants import *
from bridge.models import find_tasks, find_done_tasks
from ltibridge.settings import SERVER_URL
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)
def get_tasks_result_url(name:str,user_id):
    name = ' '.join([name[0:9],name[9:len(name)]])
    quiz = list(filter(lambda x: x['name'] == name, moodle_api.get_quizzes_by_courses(
        'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
        '7be25066e116fb2a4cf12d9441f2675c', 2)['quizzes']))[0]
    attempt_id = moodle_api.get_user_attempts(
        'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
        '7be25066e116fb2a4cf12d9441f2675c', user_id, quiz['id'])['attempts'][0]['id']
    return mark_safe(f"https://194.85.169.105:80/mod/quiz/review.php?attempt={attempt_id}&cmid={quiz['coursemodule']}")
@csrf_exempt
def graph(request):
    user = moodle_api.get_user(
        'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
        '7be25066e116fb2a4cf12d9441f2675c', 'solodkovnikita08@gmail.com')
    user_id = user['id']
    lunch_url = 'https://194.85.169.105:80/enrol/lti/tool.php?id=36'
    # generate login parameters
    consumer_secret = '3kyGn0yqqH9UsjqzM71kfj1Bm3niApJR'
    tool_consumser = ToolConsumer(consumer_key='50116f79-0e69-4556-b800-d3ed286bb419',
                            launch_url=lunch_url,
                            consumer_secret=consumer_secret,
                            params={'lti_message_type': 'basic-lti-launch-request',
                                    'lti_version': 'LTI-1p0',
                                    'tool_consumer_info_product_family_code': 'moodle',
                                    'roles': 'Student',
                                    FIRST_NAME: user['firstname'],
                                    LAST_NAME: user['lastname'],
                                    EMAIL: user['email'],
                                    'resource_link_id': str(uuid.uuid4())})

    '''
    quiz = list(filter(lambda x: x['name'] == 'Структуры 37', moodle_api.get_quizzes_by_courses(
        'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
        '7be25066e116fb2a4cf12d9441f2675c', 2)['quizzes']))[0]
    attempt_id = moodle_api.get_user_attempts(
        'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
        '7be25066e116fb2a4cf12d9441f2675c', user_id, quiz['id'])['attempts'][0]['id']
    '''
    #quiz, attempt_id = get_tasks_result_url(tasks[0].label, user_id)
    return render(
        request,
        'bridge/graph.html',
        {
            'launch_data': tool_consumser.generate_launch_data(),
            'launch_url': tool_consumser.launch_url,
            'review_url': get_tasks_result_url(request.GET.get("name"),request.GET.get("user"))
        }
    )
def get_tree():
    api_url = 'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}'
    token = '7be25066e116fb2a4cf12d9441f2675c'
    user = moodle_api.get_user(
        'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
        '7be25066e116fb2a4cf12d9441f2675c', 'solodkovnikita08@gmail.com')
    user_id = user['id']
    tasks = list(find_done_tasks('solodkovnikita08@gmail.com', 'Структуры'))
    list_of_tasks = []
    for i in tasks:
        name = ' '.join([i.label[0:9], i.label[9:len(i.label)]])
        temp = {}
        temp["name"] = i.label
        temp["url"] = "http://127.0.0.1:8000/bridge/graph"
        temp["parent"] = "Практические задания"
        quiz_id = list(filter(lambda x: x['name'] == name, moodle_api.get_quizzes_by_courses(
            api_url, token, 2)['quizzes']))[0]['id']
        temp["res"] = moodle_api.get_best_grade(api_url, token, user_id, quiz_id)
        list_of_tasks.append(temp)
    return list_of_tasks


@csrf_exempt
def test_html(request):
    api_url = 'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}'
    token = '7be25066e116fb2a4cf12d9441f2675c'
    user = moodle_api.get_user(
        'https://194.85.169.105:80/webservice/rest/server.php?moodlewsrestformat=json&wstoken={0}&wsfunction={1}',
        '7be25066e116fb2a4cf12d9441f2675c', 'solodkovnikita08@gmail.com')
    user_id = user['id']
    tasks = list(find_done_tasks('solodkovnikita08@gmail.com', 'Структуры'))
    list_of_tasks = []
    for i in tasks:
        name = ' '.join([i.label[0:9],i.label[9:len(i.label)]])
        temp = {}
        temp["name"] = i.label
        temp["url"] = mark_safe(f"http://127.0.0.1:8000/bridge/graph?name={i.label}&user={user_id}")
        temp["parent"] = "Практические задания"
        quiz_id = list(filter(lambda x: x['name'] == name, moodle_api.get_quizzes_by_courses(
            api_url,token, 2)['quizzes']))[0]['id']
        temp["res"] = moodle_api.get_best_grade(api_url,token,user_id,quiz_id)
        list_of_tasks.append(temp)
    return  render(request,'bridge/test_tree.html',{'tasks_tree':list_of_tasks, 'tasks_tree_size':len(list_of_tasks)})
@csrf_exempt
def home_vis(request):
    return render(request, 'bridge/home.html', {})
@csrf_exempt
def sunburst(request):
    return render(request, 'bridge/sunburst.html', {})

@csrf_exempt
def provider(request):
    if request.method == 'POST':
        logger.info('Incoming request from ' + urlparse(request.POST[OUTCOME_URL]).netloc)
        source = models.get_source(urlparse(request.POST[OUTCOME_URL]).netloc)

        internal_user = moodle_api.get_user(source.api_url, source.token, request.POST[EMAIL])
        request.session['source_url'] = source.api_url
        request.session['source_token'] = source.token

        if not internal_user:
            user_create_request = {
                FIRST_NAME: request.POST[FIRST_NAME],
                LAST_NAME: request.POST[LAST_NAME],
                EMAIL: request.POST[EMAIL]
            }
            logger.info('User was not found in moodle create a new one' + str(user_create_request))
            models.create_user(user_create_request)
            request.session['user_id'] = None
        else:
            logger.info('User was found in moodle ' + str(internal_user))
            request.session['user_id'] = internal_user['id']

        request.session['user_data'] = {
            FIRST_NAME: request.POST[FIRST_NAME],
            LAST_NAME: request.POST[LAST_NAME],
            EMAIL: request.POST[EMAIL],
            TITLE: request.POST['resource_link_title']
        }

        return render(
            request,
            'bridge/provider.html',
            {
                'grade_url': SERVER_URL + '/bridge/grade'
            }
        )
    return HttpResponse('')


@csrf_exempt
def progress(request):
    return JsonResponse(show_progress(request.session['user_data']))


@csrf_exempt
def grade(request):
    user_data = request.session['user_data']

    if not request.session['user_id']:
        user_id = moodle_api.get_user(request.session['source_url'],
                                      request.session['source_token'],
                                      user_data[EMAIL])['id']
    else:
        user_id = request.session['user_id']

    user = models.get_user(user_data[EMAIL])

    task_label = request.session['task_label']
    task = models.get_task(task_label)

    if user.did.get(task, 'grade'):
        return JsonResponse(user.did.get(task, 'grade'))

    user_best_grade = moodle_api.get_best_grade(request.session['source_url'],
                                                request.session['source_token'],
                                                user_id, request.session['quiz_id'])

    if user_best_grade != -1:
        models.update_user(engine.commit_result(user, task, user_best_grade))

        if user_best_grade == 0:
            JsonResponse({})
        else:
            return JsonResponse({
                'grade': user.did.get(task, 'grade')
            })

    return JsonResponse({})


def consumer(request):
    # try:
    activity, quiz_id = get_activity(request)
    # except Exception as e:
    #     print(e)
    #     return render(request, 'bridge/error.html')

    if not activity:
        return render(request, 'bridge/provider_finish.html')

    request.session['quiz_id'] = quiz_id

    return render(
        request,
        'bridge/consumer.html',
        {
            'launch_data': activity.generate_launch_data(),
            'launch_url': activity.launch_url,
            'grade_url': SERVER_URL + '/bridge/grade'
        }
    )


def get_activity(request):
    user_data = request.session['user_data']

    task = get_current_task(user_data)
    if not task:
        return None, None

    request.session['task_label'] = task.label
    logger.info('Launch url for current task ' + task.launch_url)
    return ToolConsumer(
        consumer_key=list(task.source)[0].key,
        launch_url=task.launch_url,
        consumer_secret=task.secret,
        params={
            'lti_message_type': 'basic-lti-launch-request',
            'lti_version': 'LTI-1p0',
            'tool_consumer_info_product_family_code': 'moodle',
            'roles': 'Student',
            FIRST_NAME: user_data[FIRST_NAME],
            LAST_NAME: user_data[LAST_NAME],
            EMAIL: user_data[EMAIL],
            'resource_link_id': str(uuid.uuid4())
        }
    ), task.quiz_id


def get_current_task(user_data):
    if not models.get_user(user_data[EMAIL]):
        logger.error('User was not found in graph')
        # TODO Try to sync user in mooodle and model
        logger.info('Try to create a User ' + user_data)
        user_create_request = {
            FIRST_NAME: user_data[FIRST_NAME],
            LAST_NAME: user_data[LAST_NAME],
            EMAIL: user_data[EMAIL]
        }
        models.create_user(user_create_request)

    tasks = models.find_tasks(user_data[EMAIL], user_data[TITLE])
    return engine.select_activity(tasks, user_data=user_data)


def show_progress(user_data):
    return models.get_results(user_data[EMAIL], user_data[TITLE])
