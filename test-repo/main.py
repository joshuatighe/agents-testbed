"""Entry point: wires storage -> service -> cli and runs a short demo."""

import sys

sys.dont_write_bytecode = True  # keep __pycache__ out of the workspace

from storage import InMemoryStorage
from service import TaskService
from cli import print_tasks, print_summary


def main():
    service = TaskService(InMemoryStorage())

    service.create_task("Write unit tests", priority=1)
    service.create_task("Update README", priority=3)
    service.create_task("Fix login bug", priority=1)
    service.create_task("Refactor storage layer", priority=2)

    service.complete_task(1)

    print_tasks(service)
    print_summary(service)


if __name__ == "__main__":
    main()
