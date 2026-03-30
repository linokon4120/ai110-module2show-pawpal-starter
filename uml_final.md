# PawPal+ Final UML — Class Diagram

Paste the Mermaid code below into https://mermaid.live to render and export as PNG.

```mermaid
classDiagram
    class Task {
        +str name
        +str category
        +int duration_minutes
        +int priority
        +bool is_required
        +str task_id
        +bool completed
        +str start_time
        +str frequency
        +str due_date
        +is_higher_priority_than(other) bool
        +mark_complete()
    }

    class Pet {
        +str name
        +str species
        +float age
        +str notes
        +list~Task~ tasks
        +add_task(task)
        +remove_task(task_id)
        +get_tasks() list~Task~
        +__repr__() str
    }

    class Owner {
        +str name
        +int available_minutes
        +list~Pet~ pets
        +add_pet(pet)
        +remove_pet(name)
        +get_pet(name) Pet
        +get_all_tasks() list~Task~
        +__repr__() str
    }

    class Scheduler {
        +Owner owner
        +add_task(task, pet_name)
        +remove_task(task_id)
        +sort_tasks_by_time() list~Task~
        +filter_tasks(pet_name, completed) list~Task~
        +mark_task_complete(task_id) Task
        +detect_conflicts() list~str~
        +generate_plan() DailyPlan
        -_has_time_for(task, remaining) bool
    }

    class DailyPlan {
        +list~Task~ scheduled_tasks
        +list~Task~ skipped_tasks
        +list~str~ reasoning
        +Owner owner
        +summary(show_reasoning) str
    }

    Pet "1" --> "*" Task : owns
    Owner "1" --> "*" Pet : manages
    Scheduler --> Owner : reads
    Scheduler ..> DailyPlan : creates
    DailyPlan --> Owner : references
    DailyPlan --> Task : references
```

## Key changes from initial design

| Initial | Final | Reason |
|---|---|---|
| `Pet` was a dataclass with no tasks | `Pet` is a regular class that owns `list[Task]` | Tasks belong to pets, not the scheduler |
| `Owner` held one pet | `Owner` manages `list[Pet]` | Multi-pet support added |
| `Scheduler` held its own task list | `Scheduler` reads tasks from `owner.pets` | Removes duplicate state |
| `Task` had 6 fields | `Task` has 10 fields | Added `completed`, `start_time`, `frequency`, `due_date` for Phase 3 features |
| `Scheduler` had 4 methods | `Scheduler` has 8 methods | Added sorting, filtering, recurrence, conflict detection |
| `DailyPlan` held `owner` + `pet` | `DailyPlan` holds only `owner` | Multi-pet makes pet-level reference wrong scope |
