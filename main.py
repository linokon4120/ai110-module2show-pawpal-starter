from pawpal_system import Task, Pet, Owner, Scheduler

# ---------------------------------------------------------------------------
# Setup: owner + two pets
# ---------------------------------------------------------------------------
owner = Owner(name="Alex", available_minutes=90)

dog = Pet(name="Biscuit", species="Dog", age=3)
cat = Pet(name="Mochi", species="Cat", age=5, notes="Indoor only, sensitive stomach")

owner.add_pet(dog)
owner.add_pet(cat)

# ---------------------------------------------------------------------------
# Tasks — added OUT OF ORDER to test sorting
# ---------------------------------------------------------------------------
dog.add_task(Task(
    name="Evening walk",
    category="walk",
    duration_minutes=30,
    priority=2,
    task_id="dog-walk-evening",
    start_time="17:00",
    frequency="daily",
    due_date="2026-03-30",
))
dog.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration_minutes=10,
    priority=1,
    is_required=True,
    task_id="dog-breakfast",
    start_time="07:30",
    frequency="daily",
    due_date="2026-03-30",
))
dog.add_task(Task(
    name="Morning walk",
    category="walk",
    duration_minutes=30,
    priority=1,
    is_required=True,
    task_id="dog-walk-morning",
    start_time="08:00",
    frequency="daily",
    due_date="2026-03-30",
))
dog.add_task(Task(
    name="Fetch in backyard",
    category="enrichment",
    duration_minutes=20,
    priority=3,
    task_id="dog-fetch",
    start_time="16:30",   # overlaps Evening walk at 17:00 — intentional for conflict demo
))

cat.add_task(Task(
    name="Morning feeding",
    category="feeding",
    duration_minutes=5,
    priority=1,
    is_required=True,
    task_id="cat-breakfast",
    start_time="07:00",
    frequency="daily",
    due_date="2026-03-30",
))
cat.add_task(Task(
    name="Medication",
    category="medication",
    duration_minutes=5,
    priority=1,
    is_required=True,
    task_id="cat-meds",
    start_time="07:05",   # overlaps Morning feeding — intentional for conflict demo
))
cat.add_task(Task(
    name="Grooming brush",
    category="grooming",
    duration_minutes=15,
    priority=2,
    task_id="cat-groom",
    start_time="10:00",
))
cat.add_task(Task(
    name="Play with wand toy",
    category="enrichment",
    duration_minutes=20,
    priority=3,
    task_id="cat-play",
    start_time="15:00",
))

scheduler = Scheduler(owner=owner)

# ---------------------------------------------------------------------------
# 1. Generate and print the daily plan
# ---------------------------------------------------------------------------
print("\n=== DAILY PLAN ===")
plan = scheduler.generate_plan()
print(plan.summary())

# ---------------------------------------------------------------------------
# 2. Sort all tasks by start_time
# ---------------------------------------------------------------------------
print("\n=== TASKS SORTED BY TIME ===")
for task in scheduler.sort_tasks_by_time():
    time_label = task.start_time if task.start_time else "unscheduled"
    print(f"  {time_label}  [{task.category}] {task.name} ({task.duration_minutes} min)")

# ---------------------------------------------------------------------------
# 3. Filter: show only Biscuit's tasks / only incomplete tasks
# ---------------------------------------------------------------------------
print("\n=== FILTER: Biscuit's tasks only ===")
for task in scheduler.filter_tasks(pet_name="Biscuit"):
    print(f"  {task.name}  (completed: {task.completed})")

print("\n=== FILTER: incomplete tasks across all pets ===")
for task in scheduler.filter_tasks(completed=False):
    print(f"  {task.name}")

# ---------------------------------------------------------------------------
# 4. Recurring tasks — mark Biscuit's morning walk complete
# ---------------------------------------------------------------------------
print("\n=== RECURRING: mark 'dog-walk-morning' complete ===")
next_task = scheduler.mark_task_complete("dog-walk-morning")
if next_task:
    print(f"  Next occurrence created: '{next_task.name}' due {next_task.due_date}")

# Confirm original is done and new one is pending
print("\n=== FILTER: Biscuit's tasks after completion ===")
for task in scheduler.filter_tasks(pet_name="Biscuit"):
    status = "done" if task.completed else "pending"
    print(f"  [{status}] {task.name}  (due: {task.due_date or 'n/a'})")

# ---------------------------------------------------------------------------
# 5. Conflict detection
# ---------------------------------------------------------------------------
print("\n=== CONFLICT DETECTION ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  ⚠  {warning}")
else:
    print("  No conflicts found.")
