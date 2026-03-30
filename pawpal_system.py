from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str
    age: float
    notes: str = ""


@dataclass
class Task:
    name: str
    category: str
    duration_minutes: int
    priority: int          # 1 = high, 2 = medium, 3 = low
    is_required: bool = False

    def is_higher_priority_than(self, other: "Task") -> bool:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes

    def has_time_for(self, task: Task) -> bool:
        pass

    def __repr__(self) -> str:
        pass


class DailyPlan:
    def __init__(
        self,
        scheduled_tasks: list[Task],
        skipped_tasks: list[Task],
        reasoning: list[str],
    ):
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.reasoning = reasoning

    def summary(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, name: str) -> None:
        pass

    def generate_plan(self) -> DailyPlan:
        pass
