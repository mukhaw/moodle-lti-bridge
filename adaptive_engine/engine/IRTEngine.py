from adaptive_engine.engine.IEngine import IEngine


class IRTEngine(IEngine):

    def select_activity(self, activities, **params):
        raise NotImplementedError()

    def commit_result(self, user, task, grade):
        raise NotImplementedError()
