import logging

from py2neo.ogm import Model, Property, RelatedFrom, RelatedTo

from ltibridge.settings import graph

logger = logging.getLogger(__name__)

class Topic(Model):
    __primarykey__ = "label"

    label = Property()
    sub_descriptors = RelatedTo("SubDescriptor", "related")


class SubDescriptor(Model):
    __primarykey__ = "label"

    label = Property()
    sub_descriptor = RelatedFrom("SubDescriptor", "sub_of")
    tasks = RelatedFrom("Task", "develop")


class TaskSource(Model):
    __primarykey__ = "label"

    label = Property()
    api_url = Property("api_url")
    key = Property("key")
    token = Property("token")


class Task(Model):
    __primarykey__ = "label"

    label = Property()
    launch_url = Property("launch_url")
    quiz_id = Property("quiz_id")
    secret = Property("secret")
    sub_descriptor = RelatedTo("SubDescriptor", "develop")
    source = RelatedFrom("TaskSource", "contains")

    def __hash__(self):
        return int(self.quiz_id)


class User(Model):
    __primarykey__ = "email"

    user_id = Property("user_id")
    first_name = Property("first_name")
    last_name = Property("last_name")
    email = Property("email")
    knows = RelatedTo("SubDescriptor", "know")
    did = RelatedTo("Task", "did")


def create_user(user_data):
    user = User()
    user.first_name = user_data['lis_person_name_given']
    user.last_name = user_data['lis_person_name_family']
    user.email = user_data['lis_person_contact_email_primary']
    graph.push(user)


def update_user(user):
    graph.push(user)


def get_task(label):
    return Task.match(graph, label).first()


def get_user(email):
    return User.match(graph, email).first()


def get_source(host):
    return TaskSource.match(graph, host).first()


def find_tasks(email, topic):
    user = User.match(graph, email).first()

    topic = Topic.match(graph, topic).first()

    if not topic:
        return None

    tasks = flat_map(lambda x: x.tasks, topic.sub_descriptors)

    return set(filter(lambda x: x not in user.did, tasks))
def find_done_tasks(email, topic):
    user = User.match(graph, email).first()

    topic = Topic.match(graph, topic).first()

    if not topic:
        return None

    tasks = flat_map(lambda x: x.tasks, topic.sub_descriptors)

    return set(filter(lambda x: x in user.did, tasks))


def find_target_descriptor(topic):
    topic = Topic.match(graph, topic).first()
    return list(filter(lambda x: topic.sub_descriptors.get(x, 'target') is True, topic.sub_descriptors))


def flat_map(f, xs):
    return [y for ys in xs for y in f(ys)]


def get_results(email, topic):
    user = get_user(email)

    topic = Topic.match(graph, topic).first()

    return {sd.label: user.knows.get(sd, 'weight') if not user.knows.get(sd, 'weight') is None else 0 for sd in
            topic.sub_descriptors}
