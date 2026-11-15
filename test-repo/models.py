"""Data models for the task tracker."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    priority: int = 2  # 1 = high, 2 = medium, 3 = low
    done: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def mark_done(self):
        self.done = True

    def __str__(self):
        status = "x" if self.done else " "
        return f"[{status}] #{self.id} (P{self.priority}) {self.title}"
