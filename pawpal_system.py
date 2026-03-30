from dataclasses import dataclass
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _time_to_minutes(hhmm: str) -> int:
    """Convert a 'HH:MM' string to minutes since midnight for numeric comparison."""
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    category: str           # e.g. walk, feeding, medication, grooming, enrichment
    duration_minutes: int
    priority: int           # 1 = high, 2 = medium, 3 = low
    is_required: bool = False
    task_id: str = ""       # unique identifier; set by caller to avoid name collisions
    completed: bool = False
    start_time: str = ""    # "HH:MM" — scheduled start; empty means unscheduled
    frequency: str = "none" # "none" | "daily" | "weekly"
    due_date: str = ""      # "YYYY-MM-DD" — empty means no due date

    def is_higher_priority_than(self, other: "Task") -> bool:
        """Return True if this task has a higher priority (lower number) than other."""
        return self.priority < other.priority

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

class Pet:
    """Stores pet details and owns the pet's list of care tasks."""

    def __init__(self, name: str, species: str, age: float, notes: str = ""):
        """Initialize a Pet with identifying details and an empty task list."""
        self.name = name
        self.species = species
        self.age = age
        self.notes = notes
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given task_id. No-op if not found."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return a shallow copy of this pet's task list."""
        return list(self.tasks)

    def __repr__(self) -> str:
        """Return a concise string representation of this Pet."""
        return (
            f"Pet(name={self.name!r}, species={self.species!r}, "
            f"age={self.age}, tasks={len(self.tasks)})"
        )


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Manages one or more pets and exposes a unified view of all their tasks."""

    def __init__(self, name: str, available_minutes: int):
        """Initialize an Owner with a name and a daily care time budget in minutes."""
        self.name = name
        self.available_minutes = available_minutes  # total daily care budget
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove the first pet with the given name."""
        self.pets = [p for p in self.pets if p.name != name]

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name; returns None if not found."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Collect and return every task across all pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def __repr__(self) -> str:
        """Return a concise string representation of this Owner."""
        return (
            f"Owner(name={self.name!r}, available_minutes={self.available_minutes}, "
            f"pets={len(self.pets)})"
        )


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------

class DailyPlan:
    """Output object produced by Scheduler.generate_plan()."""

    def __init__(
        self,
        scheduled_tasks: list[Task],
        skipped_tasks: list[Task],
        reasoning: list[str],
        owner: Owner,
    ):
        """Store the results of a scheduling run, including skipped tasks and reasoning."""
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.reasoning = reasoning
        self.owner = owner

    def summary(self, show_reasoning: bool = False) -> str:
        """Format the plan as a readable terminal output.

        Args:
            show_reasoning: If True, append a full decision log at the bottom.
        """
        divider = "-" * 44
        header = f"  Daily Care Plan — {self.owner.name}"
        lines = [divider, header, divider]

        # --- Scheduled ---
        total_minutes = sum(t.duration_minutes for t in self.scheduled_tasks)
        budget = self.owner.available_minutes
        lines.append(f"\n  SCHEDULED  ({total_minutes} / {budget} min used)\n")

        if self.scheduled_tasks:
            for task in self.scheduled_tasks:
                flag = "(!)" if task.is_required else "   "
                name_col = task.name.ljust(24)
                dur_col = f"{task.duration_minutes} min".rjust(6)
                time_col = f"  @ {task.start_time}" if task.start_time else ""
                lines.append(f"  {flag}  {name_col}  {dur_col}  {task.category}{time_col}")
        else:
            lines.append("  No tasks could be scheduled.")

        # --- Skipped ---
        if self.skipped_tasks:
            lines.append(f"\n  SKIPPED\n")
            for task in self.skipped_tasks:
                name_col = task.name.ljust(24)
                dur_col = f"{task.duration_minutes} min".rjust(6)
                lines.append(f"       {name_col}  {dur_col}")

        lines.append(f"\n{divider}")

        # --- Optional reasoning log ---
        if show_reasoning and self.reasoning:
            lines.append("\n  REASONING\n")
            for reason in self.reasoning:
                lines.append(f"  • {reason}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Retrieves tasks from the owner's pets, organizes them, and builds a DailyPlan."""

    def __init__(self, owner: Owner):
        """Initialize the Scheduler with an Owner whose pets and tasks it will manage."""
        self.owner = owner

    # --- Task management ---

    def add_task(self, task: Task, pet_name: str) -> None:
        """Add a task to a specific pet by name."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"No pet named {pet_name!r} found under {self.owner.name!r}.")
        pet.add_task(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by task_id across all of the owner's pets."""
        for pet in self.owner.pets:
            pet.remove_task(task_id)

    # --- Sorting ---

    def sort_tasks_by_time(self) -> list[Task]:
        """Return all tasks sorted by start_time (HH:MM); unscheduled tasks go last."""
        all_tasks = self.owner.get_all_tasks()
        scheduled = [t for t in all_tasks if t.start_time]
        unscheduled = [t for t in all_tasks if not t.start_time]
        scheduled.sort(key=lambda t: _time_to_minutes(t.start_time))
        return scheduled + unscheduled

    # --- Filtering ---

    def filter_tasks(
        self,
        *,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks matching the given filters.

        Args:
            pet_name:  If provided, only include tasks belonging to this pet.
            completed: If True, return only completed tasks; if False, only incomplete.
                       If None, completion status is not filtered.
        """
        results: list[Task] = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    # --- Recurring tasks ---

    def mark_task_complete(self, task_id: str) -> Task | None:
        """Mark a task complete and, if recurring, add the next occurrence to the same pet.

        Returns:
            The newly created next-occurrence Task if the task is recurring, else None.
        """
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.task_id != task_id:
                    continue
                task.mark_complete()
                if task.frequency == "none":
                    return None
                delta = timedelta(days=1 if task.frequency == "daily" else 7)
                base = date.fromisoformat(task.due_date) if task.due_date else date.today()
                next_due = base + delta
                next_task = Task(
                    name=task.name,
                    category=task.category,
                    duration_minutes=task.duration_minutes,
                    priority=task.priority,
                    is_required=task.is_required,
                    task_id=f"{task.task_id}-{next_due.isoformat()}",
                    completed=False,
                    start_time=task.start_time,
                    frequency=task.frequency,
                    due_date=next_due.isoformat(),
                )
                pet.add_task(next_task)
                return next_task
        return None

    # --- Conflict detection ---

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for any tasks on the same pet with overlapping time windows.

        Only tasks with a start_time are checked; unscheduled tasks are ignored.
        Overlap is defined as: task1 starts before task2 ends AND task2 starts before task1 ends.
        """
        warnings: list[str] = []
        for pet in self.owner.pets:
            scheduled = [t for t in pet.tasks if t.start_time]
            for i, t1 in enumerate(scheduled):
                for t2 in scheduled[i + 1:]:
                    s1 = _time_to_minutes(t1.start_time)
                    e1 = s1 + t1.duration_minutes
                    s2 = _time_to_minutes(t2.start_time)
                    e2 = s2 + t2.duration_minutes
                    if s1 < e2 and s2 < e1:
                        warnings.append(
                            f"Conflict [{pet.name}]: '{t1.name}' ({t1.start_time}, "
                            f"{t1.duration_minutes} min) overlaps '{t2.name}' "
                            f"({t2.start_time}, {t2.duration_minutes} min)."
                        )
        return warnings

    # --- Plan generation ---

    def _has_time_for(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits within the remaining time budget."""
        return task.duration_minutes <= remaining_minutes

    def generate_plan(self) -> DailyPlan:
        """Build a daily schedule from all tasks across all pets.

        Strategy:
          1. Required tasks are always scheduled first, regardless of time.
          2. Optional tasks are sorted by priority (1=high first), then by
             duration (shorter first) as a tiebreaker to maximise tasks fit.
          3. An optional task is skipped if it no longer fits in the remaining budget.
        """
        all_tasks = self.owner.get_all_tasks()
        required = [t for t in all_tasks if t.is_required]
        optional = [t for t in all_tasks if not t.is_required]

        # Sort optional: highest priority first; shorter tasks break ties
        optional.sort(key=lambda t: (t.priority, t.duration_minutes))

        scheduled: list[Task] = []
        skipped: list[Task] = []
        reasoning: list[str] = []
        remaining = self.owner.available_minutes

        # --- Required tasks ---
        for task in required:
            scheduled.append(task)
            remaining -= task.duration_minutes
            reasoning.append(
                f"'{task.name}' scheduled — required task (priority {task.priority})."
            )

        if remaining < 0:
            reasoning.append(
                f"Warning: required tasks alone exceed the daily budget by {abs(remaining)} min."
            )

        # --- Optional tasks ---
        for task in optional:
            if self._has_time_for(task, remaining):
                scheduled.append(task)
                remaining -= task.duration_minutes
                reasoning.append(
                    f"'{task.name}' scheduled ({task.duration_minutes} min, "
                    f"priority {task.priority}). {remaining} min remaining."
                )
            else:
                skipped.append(task)
                reasoning.append(
                    f"'{task.name}' skipped — needs {task.duration_minutes} min "
                    f"but only {remaining} min left."
                )

        return DailyPlan(
            scheduled_tasks=scheduled,
            skipped_tasks=skipped,
            reasoning=reasoning,
            owner=self.owner,
        )
