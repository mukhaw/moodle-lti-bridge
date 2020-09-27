from abc import ABCMeta, abstractmethod


class IEngine(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def select_activity(self, activities, **params):
        """
        Select a current activity from the activities that are given by bridge.

        :param activities: activities that are given by bridge
        :return: selected activity_id
        """
        raise NotImplementedError("Adaptive Engine driver must implement this method.")

    @abstractmethod
    def commit_result(self, user, task, grade):
        """
        Evaluate task impact for user knowledge.

        :param user: student to evaluate
        :param task: submitted task
        :param grade: grade of the task
        :return updated_user: SequenceItem instance
        """
        raise NotImplementedError("Adaptive Engine driver must implement this method.")
