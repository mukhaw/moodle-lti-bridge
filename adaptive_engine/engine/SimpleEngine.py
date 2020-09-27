from adaptive_engine.engine.IEngine import IEngine


class SimpleEngine(IEngine):

    def select_activity(self, activities, **params):
        if not activities:
            return None
        return activities[0]

    def commit_result(self, user, task, grade):
        if not grade > 0:
            return user

        user.did.add(task, properties={'grade': grade})

        for sd in task.sub_descriptor:
            task.sub_descriptor.get(sd, 'weight')

            sd_tasks = set(map(lambda x: x.label, sd.tasks))
            user_tasks = set(map(lambda x: x.label, user.did))

            sd_tasks.difference(user_tasks)

            complete_rate = len(user_tasks.intersection(sd_tasks)) / len(sd_tasks)

            user.knows.update(sd, properties={'weight': complete_rate})

        return user
