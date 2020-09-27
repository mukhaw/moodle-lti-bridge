from py2neo import Graph
from py2neo.ogm import Model, Property, RelatedFrom, RelatedTo


class Topic(Model):
    __primarykey__ = "label"

    label = Property()
    sub_descriptors = RelatedTo("SubDescriptor", "related")


class SubDescriptor(Model):
    __primarykey__ = "label"

    label = Property()
    sub_descriptor = RelatedFrom("SubDescriptor", "sub_of")
    tasks = RelatedFrom("Task", "develop")


class Task(Model):
    __primarykey__ = "label"

    label = Property()
    launch_url = Property("launch_url")
    quiz_id = Property("quiz_id")
    sub_descriptor = RelatedTo("SubDescriptor", "develop")


class User(Model):
    __primarykey__ = "email"

    user_id = Property("user_id")
    first_name = Property("first_name")
    last_name = Property("last_name")
    email = Property("email")
    knows = RelatedTo("SubDescriptor", "know")
    did = RelatedTo("Task", "did")


def get_results(email, topic):
    user = User.match(graph, email).first()

    topic = Topic.match(graph, topic).first()

    return {sd.label: user.knows.get(sd, 'weight') if not user.knows.get(sd, 'weight') is None else 0 for sd in
            topic.sub_descriptors}


host = "bolt://neo4j:test@localhost:7687"
graph = Graph(host)

# OGM(first_sub_descriptor).related(INCOMING, "develop", "Task")
#
# for sub_descriptor in first_sub_descriptor.tasks:
#     first_sub_descriptor.tasks.get(sub_descriptor, 'weight')
#
#     print(sub_descriptor.launch_url)


label = 'Знает основные операции над вещественными, строками, операции целочисленной арифметики.'
sd = SubDescriptor.match(graph, label).first()

user = User()

task1 = Task.match(graph, 'Базовые типы данных1').first()
task2 = Task.match(graph, 'Базовые типы данных2').first()
task3 = Task.match(graph, 'Базовые типы данных3').first()
task4 = Task.match(graph, 'Базовые типы данных4').first()

user.did.add(task1, properties={'grade': '1'})

sd_tasks = set(map(lambda x: x.label, list(sd.tasks)))
user_tasks = set(map(lambda x: x.label, list(user.did)))

sd_tasks.difference(user_tasks)

complete_rate = len(user_tasks.intersection(sd_tasks)) / len(sd_tasks)

graph.push(user)
# flat_map = lambda f, xs: [y for ys in xs for y in f(ys)]
# tasks = flat_map(lambda x: x.tasks, Topic.match(graph, 'Test LTI provider').first().sub_descriptors)
#
# list(filter(lambda x: x not in user.did, tasks))
# Topic.match(graph, 'Test LTI provider').first().sub_descriptors
#
#
# Topic.match(graph, 'Test LTI provider')


# user = User()
# user.user_id = '1'
# user.first_name = 'Test'
# user.last_name = 'Test'
# user.knows.add(first_sub_descriptor, properties={'weight': 0.8})
# graph.push(user)

# created_user = User.match(graph, "1").first()
# print(created_user)
#
# rel = Relationship(created_user, 'know', first_sub_descriptor)


# graph.delete(user)
