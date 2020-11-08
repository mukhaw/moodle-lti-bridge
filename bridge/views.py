import logging
import uuid
from urllib.parse import urljoin, urlparse

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from lti import ToolConsumer

from bridge import moodle_api, models, engine
from bridge.constants import *

logger = logging.getLogger(__name__)


@csrf_exempt
def provider(request):
    if request.method == 'POST':
        logger.info(request.POST)
        logger.info(urlparse(request.POST[OUTCOME_URL]).netloc)

        source = models.get_source(urlparse(request.POST[OUTCOME_URL]).netloc)

        internal_user = moodle_api.get_user(source.api_url, source.token, request.POST[EMAIL])
        request.session['source_url'] = source.api_url
        request.session['source_token'] = source.token

        if not internal_user:
            models.create_user({
                FIRST_NAME: request.POST[FIRST_NAME],
                LAST_NAME: request.POST[LAST_NAME],
                EMAIL: request.POST[EMAIL]
            })
            request.session['user_id'] = None
        else:
            request.session['user_id'] = internal_user['id']

        request.session['user_data'] = {
            FIRST_NAME: request.POST[FIRST_NAME],
            LAST_NAME: request.POST[LAST_NAME],
            EMAIL: request.POST[EMAIL],
            TITLE: request.POST['resource_link_title']
        }

        grade_url = urljoin(settings.BRIDGE_HOST, reverse('bridge:grade'))
        logger.debug(grade_url)
        return render(
            request,
            'bridge/provider.html',
            {
                'grade_url': grade_url
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
    try:
        activity, quiz_id = get_activity(request)
    except Exception:
        return render(request, 'bridge/error.html')

    if not activity:
        return render(request, 'bridge/provider_finish.html')

    request.session['quiz_id'] = quiz_id

    return render(
        request,
        'bridge/consumer.html',
        {
            'launch_data': activity.generate_launch_data(),
            'launch_url': activity.launch_url,
            'grade_url': urljoin(settings.BRIDGE_HOST, reverse('bridge:grade'))
        }
    )


def get_activity(request):
    user_data = request.session['user_data']

    task = get_current_task(user_data)
    if not task:
        return None, None

    request.session['task_label'] = task.label
    print(task.launch_url)
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
    tasks = models.find_tasks(user_data[EMAIL], user_data[TITLE])
    return engine.select_activity(tasks, user_data=user_data)


def show_progress(user_data):
    return models.get_results(user_data[EMAIL], user_data[TITLE])
