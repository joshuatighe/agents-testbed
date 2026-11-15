"""Presentation layer: formats service output for the terminal."""


def print_tasks(service):
    tasks = service.pending_tasks()
    if not tasks:
        print("No pending tasks.")
        return
    print("Pending tasks:")
    for task in tasks:
        print(f"  {task}")


def print_summary(service):
    s = service.summary()
    print(f"Total: {s['total']} | Done: {s['done']} | Pending: {s['pending']}")
