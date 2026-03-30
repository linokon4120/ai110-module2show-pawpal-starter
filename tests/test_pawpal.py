from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip completed from False to True."""
    task = Task(name="Morning walk", category="walk", duration_minutes=30, priority=1)

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Biscuit", species="Dog", age=3)
    task = Task(name="Breakfast", category="feeding", duration_minutes=10, priority=1)

    before = len(pet.get_tasks())
    pet.add_task(task)
    after = len(pet.get_tasks())

    assert after == before + 1
