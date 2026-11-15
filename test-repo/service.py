"""Business logic for managing tasks. Depends only on a storage object."""


class TaskService:
    def __init__(self, storage):
        self.storage = storage

    def create_task(self, title, priority=2):
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")
        if priority not in (1, 2, 3):
            raise ValueError("Priority must be 1, 2, or 3")
        return self.storage.add(title, priority)

    def complete_task(self, task_id):
        task = self.storage.get(task_id)
        if task is None:
            raise KeyError(f"No task with id {task_id}")
        task.mark_done()
        return task

    def remove_task(self, task_id):
        return self.storage.delete(task_id)

    def pending_tasks(self):
        """Unfinished tasks, highest priority first."""
        tasks = [t for t in self.storage.all() if not t.done]
        return sorted(tasks, key=lambda t: (t.priority, t.id))

    def summary(self):
        tasks = self.storage.all()
        done = sum(1 for t in tasks if t.done)
        return {"total": len(tasks), "done": done, "pending": len(tasks) - done}
