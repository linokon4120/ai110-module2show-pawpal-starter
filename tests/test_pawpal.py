from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers — keep test bodies short and readable
# ---------------------------------------------------------------------------

def _task(name, *, start_time="", frequency="none", due_date="",
          priority=2, duration=20, task_id="", required=False):
    """Create a Task with sensible defaults for testing."""
    return Task(
        name=name,
        category="walk",
        duration_minutes=duration,
        priority=priority,
        is_required=required,
        task_id=task_id or name.lower().replace(" ", "-"),
        start_time=start_time,
        frequency=frequency,
        due_date=due_date,
    )


def _scheduler(*pets, minutes=120):
    """Create a Scheduler backed by an Owner with the given pets."""
    owner = Owner(name="Test Owner", available_minutes=minutes)
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)


# ---------------------------------------------------------------------------
# Original tests (kept and updated to use helpers)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should flip completed from False to True."""
    task = _task("Morning walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Biscuit", species="Dog", age=3)
    before = len(pet.get_tasks())
    pet.add_task(_task("Breakfast"))
    assert len(pet.get_tasks()) == before + 1


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_sort_tasks_chronological_order():
    """Tasks with start_time should come back sorted earliest-first."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(_task("Dinner", start_time="18:00"))
    pet.add_task(_task("Breakfast", start_time="07:00"))
    pet.add_task(_task("Lunch", start_time="12:00"))

    times = [t.start_time for t in _scheduler(pet).sort_tasks_by_time()]
    assert times == ["07:00", "12:00", "18:00"]


def test_sort_unscheduled_tasks_go_last():
    """Tasks without a start_time should be appended after all scheduled ones."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(_task("No Time Task"))           # no start_time
    pet.add_task(_task("Morning", start_time="08:00"))

    sorted_tasks = _scheduler(pet).sort_tasks_by_time()
    assert sorted_tasks[0].start_time == "08:00"
    assert sorted_tasks[-1].start_time == ""


def test_sort_pet_with_no_tasks_returns_empty():
    """sort_tasks_by_time on an owner with no tasks should return an empty list."""
    pet = Pet("Rex", "Dog", 2)
    assert _scheduler(pet).sort_tasks_by_time() == []


# ---------------------------------------------------------------------------
# Recurring tasks
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_day_task():
    """Completing a daily task should add a new task due the following day."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(_task("Walk", frequency="daily", due_date="2026-03-30", task_id="walk-1"))
    scheduler = _scheduler(pet)

    next_task = scheduler.mark_task_complete("walk-1")

    assert next_task is not None
    assert next_task.due_date == "2026-03-31"
    assert next_task.completed is False


def test_weekly_recurrence_creates_task_seven_days_later():
    """Completing a weekly task should add a new task due 7 days later."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(_task("Grooming", frequency="weekly", due_date="2026-03-30", task_id="groom-1"))
    scheduler = _scheduler(pet)

    next_task = scheduler.mark_task_complete("groom-1")

    assert next_task is not None
    assert next_task.due_date == "2026-04-06"


def test_non_recurring_completion_returns_none():
    """Completing a non-recurring task should return None and not add a new task."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(_task("One-off", frequency="none", task_id="one-off"))
    scheduler = _scheduler(pet)

    result = scheduler.mark_task_complete("one-off")

    assert result is None
    assert len(pet.tasks) == 1   # no extra task added


def test_original_task_marked_done_after_recurrence():
    """The original task should be completed even when a next occurrence is created."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(_task("Walk", frequency="daily", due_date="2026-03-30", task_id="walk-1"))
    _scheduler(pet).mark_task_complete("walk-1")

    assert pet.tasks[0].completed is True


def test_mark_nonexistent_task_returns_none():
    """mark_task_complete with an unknown task_id should return None silently."""
    pet = Pet("Rex", "Dog", 2)
    result = _scheduler(pet).mark_task_complete("does-not-exist")
    assert result is None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_overlapping_tasks_are_flagged():
    """Two tasks on the same pet whose windows overlap should produce a conflict warning."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(_task("Walk", start_time="08:00", duration=30, task_id="walk"))
    pet.add_task(_task("Fetch", start_time="08:15", duration=20, task_id="fetch"))

    conflicts = _scheduler(pet).detect_conflicts()

    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Fetch" in conflicts[0]


def test_adjacent_tasks_are_not_flagged():
    """Tasks that touch (one ends exactly when the next begins) should not conflict."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(_task("Walk", start_time="08:00", duration=30, task_id="walk"))   # ends 08:30
    pet.add_task(_task("Fetch", start_time="08:30", duration=20, task_id="fetch")) # starts 08:30

    assert _scheduler(pet).detect_conflicts() == []


def test_unscheduled_tasks_never_conflict():
    """Tasks without a start_time should never be flagged, even if there are many."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(_task("Task A"))
    pet.add_task(_task("Task B"))

    assert _scheduler(pet).detect_conflicts() == []


def test_cross_pet_overlaps_are_not_flagged():
    """Overlapping tasks on *different* pets should not count as conflicts."""
    dog = Pet("Biscuit", "Dog", 3)
    cat = Pet("Mochi", "Cat", 5)
    dog.add_task(_task("Dog walk", start_time="08:00", duration=30, task_id="d-walk"))
    cat.add_task(_task("Cat play", start_time="08:15", duration=30, task_id="c-play"))

    # conflict detection is per-pet; different pets can overlap the owner's clock
    assert _scheduler(dog, cat).detect_conflicts() == []


def test_no_conflicts_when_no_tasks():
    """An owner with no tasks at all should return zero conflicts."""
    pet = Pet("Rex", "Dog", 2)
    assert _scheduler(pet).detect_conflicts() == []


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def test_filter_by_pet_name_returns_only_that_pets_tasks():
    """filter_tasks(pet_name=...) should exclude tasks from all other pets."""
    dog = Pet("Biscuit", "Dog", 3)
    cat = Pet("Mochi", "Cat", 5)
    dog.add_task(_task("Dog walk", task_id="d-walk"))
    cat.add_task(_task("Cat play", task_id="c-play"))
    scheduler = _scheduler(dog, cat)

    results = scheduler.filter_tasks(pet_name="Biscuit")

    assert len(results) == 1
    assert results[0].name == "Dog walk"


def test_filter_incomplete_excludes_done_tasks():
    """filter_tasks(completed=False) should return only tasks not yet marked done."""
    pet = Pet("Rex", "Dog", 2)
    done = _task("Done task", task_id="done")
    pending = _task("Pending task", task_id="pending")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(pending)

    results = _scheduler(pet).filter_tasks(completed=False)

    assert len(results) == 1
    assert results[0].name == "Pending task"


# ---------------------------------------------------------------------------
# generate_plan edge cases
# ---------------------------------------------------------------------------

def test_generate_plan_with_no_tasks_returns_empty_plan():
    """generate_plan should not crash when the owner has no tasks."""
    owner = Owner("Alex", available_minutes=60)
    plan = Scheduler(owner).generate_plan()

    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []


def test_required_tasks_always_scheduled_even_over_budget():
    """Required tasks must appear in the plan even when they exceed available time."""
    pet = Pet("Rex", "Dog", 2)
    pet.add_task(Task(
        name="Meds",
        category="medication",
        duration_minutes=10,
        priority=1,
        is_required=True,
        task_id="meds",
    ))
    owner = Owner("Alex", available_minutes=5)  # budget too small
    owner.add_pet(pet)
    plan = Scheduler(owner).generate_plan()

    scheduled_names = [t.name for t in plan.scheduled_tasks]
    assert "Meds" in scheduled_names
