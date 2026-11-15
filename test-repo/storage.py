"""Storage layer: keeps tasks in memory.

Swap this class out for a file- or database-backed version without
changing the service layer, as long as the same methods are provided.
"""

from models import Task


class InMemoryStorage:
    def __init__(self):
        self._tasks = {}
        self._next_id = 1

    def add(self, title, priority):
        task = Task(id=self._next_id, title=title, priority=priority)
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id):
        return self._tasks.get(task_id)

    def all(self):
        return list(self._tasks.values())

    def delete(self, task_id):
        return self._tasks.pop(task_id, None) is not None
