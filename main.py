from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes=90)

dog = Pet(name="Biscuit", species="Dog", age=3)
cat = Pet(name="Mochi", species="Cat", age=5, notes="Indoor only, sensitive stomach")

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks for Biscuit (dog) ---
dog.add_task(Task(
    name="Morning walk",
    category="walk",
    duration_minutes=30,
    priority=1,
    is_required=True,
    task_id="dog-walk-morning",
))
dog.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration_minutes=10,
    priority=1,
    is_required=True,
    task_id="dog-breakfast",
))
dog.add_task(Task(
    name="Fetch in backyard",
    category="enrichment",
    duration_minutes=20,
    priority=3,
    task_id="dog-fetch",
))

# --- Tasks for Mochi (cat) ---
cat.add_task(Task(
    name="Morning feeding",
    category="feeding",
    duration_minutes=5,
    priority=1,
    is_required=True,
    task_id="cat-breakfast",
))
cat.add_task(Task(
    name="Medication",
    category="medication",
    duration_minutes=5,
    priority=1,
    is_required=True,
    task_id="cat-meds",
))
cat.add_task(Task(
    name="Grooming brush",
    category="grooming",
    duration_minutes=15,
    priority=2,
    task_id="cat-groom",
))
cat.add_task(Task(
    name="Play with wand toy",
    category="enrichment",
    duration_minutes=20,
    priority=3,
    task_id="cat-play",
))

# --- Generate and print plan ---
scheduler = Scheduler(owner=owner)
plan = scheduler.generate_plan()

print(plan.summary())
