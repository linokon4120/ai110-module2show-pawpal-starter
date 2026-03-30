# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Three core user actions:**

1. **Enter owner and pet info** — The user can provide basic details about themselves and their pet (like owner name, pet name and species, and total time available for care each day).

2. **Add and manage care tasks** — The user creates individual care tasks (walks, feeding, medication, grooming, enrichment, etc.), each with at minimum a name, estimated duration, and priority level. The user should also be able to edit or remove tasks so the list stays accurate over time.

3. **Generate and view the daily plan** — The user triggers the scheduler, which takes the task list and owner constraints, selects and orders tasks that fit within the available time window, and displays the resulting daily schedule. Ideally the app also explains why certain tasks were included or excluded (e.g., "Medication was scheduled first because it is high priority; enrichment walk was skipped because no time remained").

**Classes, attributes, and responsibilities:**

- **`Pet`** (dataclass) — pure data container for the animal being cared for. Holds `name`, `species`, `age`, and `notes` (special needs). No behavior; exists so other classes have a typed object to reference instead of loose strings.

- **`Task`** (dataclass) — the atomic unit of the system. Holds everything needed to evaluate and schedule one care activity: `name`, `category`, `duration_minutes`, `priority` (1=high, 2=medium, 3=low), `is_required` (non-negotiable tasks like medication), and `task_id` (unique key for safe removal). Has one comparison method: `is_higher_priority_than(other)`.

- **`Owner`** — holds the scheduling constraint: `name` and `available_minutes` (total daily care budget). Intentionally kept simple; time-tracking logic lives in `Scheduler`, not here.

- **`Scheduler`** — the core logic class. Owns the task list and references to `Owner` and `Pet`. Responsible for `add_task`, `remove_task` (by `task_id`), and `generate_plan`. Also has a private helper `_has_time_for(task, remaining_minutes)` that checks fit against the running time budget during plan generation.

- **`DailyPlan`** — the output object produced by `Scheduler.generate_plan()`. Holds `scheduled_tasks`, `skipped_tasks`, `reasoning` (one string per scheduling decision), and references to `owner` and `pet` so `summary()` can produce a named, context-aware output.

**b. Design changes**

After reviewing the initial skeleton, three changes were made based on AI feedback:

1. **Moved time-availability check from `Owner` to `Scheduler`** — The original design put `has_time_for(task)` on `Owner`, but `Owner` only knows the total budget, not how much has already been used. The running tally of remaining minutes only exists during `generate_plan()`, so the check was moved there as a private method `_has_time_for(task, remaining_minutes)`. This keeps `Owner` as a simple data holder and avoids giving it responsibilities that require `Scheduler`'s state.

2. **Added `task_id` to `Task` and changed `remove_task` to use it** — The original `remove_task(name)` was ambiguous if two tasks shared the same name (e.g., two "Walk" entries). Adding a `task_id` field makes removal unambiguous and mirrors how most real systems handle item identity.

3. **Added `owner` and `pet` references to `DailyPlan`** — Without these, `DailyPlan.summary()` could not produce a pet-specific or owner-specific message. Passing them in at construction time gives `summary()` the context it needs without requiring the UI layer to inject it separately.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Required flag** — tasks marked `is_required=True` are always scheduled regardless of the time budget. This was treated as the hardest constraint because dropping a medication or feeding task would have real consequences for the pet.
2. **Daily time budget** — the owner's `available_minutes` sets a hard upper limit on total scheduled time. Once the budget is exhausted, optional tasks are skipped.
3. **Priority level** — among optional tasks, those with priority 1 (high) are scheduled before priority 2 (medium) before priority 3 (low). Duration is used as a tiebreaker — shorter tasks of equal priority are scheduled first to fit more tasks in.

The required-first rule was decided first because it reflects real-world necessity. Time budget was second because it is the primary user-provided constraint. Priority ordering was third because it is a preference, not a hard rule — a low-priority task can still run if time allows.

**b. Tradeoffs**

The conflict detector checks for **exact time-window overlaps** (task A starts before task B ends, and task B starts before task A ends) but does not account for travel time, setup time, or owner fatigue between tasks. Two tasks scheduled back-to-back — one ending at 08:30 and the next starting at 08:30 — are considered non-conflicting even if the owner realistically needs a few minutes between them.

This tradeoff is reasonable for a first version because: (1) the exact overlap check covers the most obvious scheduling mistakes without requiring extra configuration; (2) adding buffer time would require the owner to specify it per task or globally, which adds friction for a daily-use tool; and (3) the scheduler's purpose is to help, not to perfectly simulate reality — a warning about an actual overlap is more useful than false positives from a buffer that may not apply to every task pair.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used at every stage of the project, but in different modes:

- **Design brainstorming (Phase 1)** — Used AI to generate a list of classes and identify missing relationships (e.g., that `has_time_for` belonged on `Scheduler`, not `Owner`). Asking "what relationships or logic bottlenecks do you see?" was more useful than asking "what should I build?" because it forced the AI to reason about the design rather than invent requirements.
- **Skeleton generation (Phase 2)** — Used AI to produce class stubs from the UML description. The most effective prompt style was giving the class diagram as context and asking for Python that matched it exactly, rather than a free-form "write me a scheduler."
- **Algorithm brainstorming (Phase 3)** — Used AI to suggest sorting, filtering, recurrence, and conflict detection strategies. Asking "give me a lightweight strategy that returns a warning string rather than raising an exception" steered it toward operationally appropriate solutions.
- **Test planning** — Used AI to enumerate edge cases ("what would break this sorting function?"). This was the highest-value use: AI is good at exhaustively listing boundary conditions, which is tedious to do manually.

**b. Judgment and verification**

The initial AI suggestion for `has_time_for` placed it as a method on `Owner`, checking whether a task fit within `owner.available_minutes`. This looked reasonable in isolation. The suggestion was rejected because `Owner.available_minutes` is a fixed total — it does not decrease as tasks are added. The running tally of remaining time only exists as a local variable inside `generate_plan()`, so putting the check on `Owner` would require either passing the tally as an argument (which defeats the encapsulation) or storing it as mutable state on `Owner` (which gives `Owner` scheduler responsibilities it shouldn't have). The fix was to move the check into `Scheduler` as the private method `_has_time_for(task, remaining_minutes)`, where the remaining budget is always in scope. This was verified by tracing through the generate_plan loop manually and confirming that `remaining` was correctly decremented after each scheduled task.

---

## 4. Testing and Verification

**a. What you tested**

19 automated tests across six areas:

1. **Task completion** — `mark_complete()` flips `completed` to `True`. Important because recurring task logic depends on this flag being accurate.
2. **Sorting correctness** — tasks come back in chronological `HH:MM` order; unscheduled tasks go last; an empty pet returns an empty list. Important because the UI displays tasks in sorted order.
3. **Recurrence logic** — daily tasks produce a next occurrence with `due_date + 1 day`; weekly tasks use `+7 days`; non-recurring tasks return `None` and add nothing; the original task is marked done. Important because silent failures here would cause tasks to disappear or duplicate incorrectly.
4. **Conflict detection** — overlapping windows are flagged; adjacent tasks (one ends exactly when the next begins) are *not* flagged; tasks on different pets are *not* flagged; unscheduled tasks are never flagged. Important for verifying the boundary conditions of the overlap check.
5. **Filtering** — `filter_tasks(pet_name=...)` returns only that pet's tasks; `filter_tasks(completed=False)` excludes done tasks. Important because the UI uses filtering to display relevant subsets.
6. **`generate_plan` edge cases** — an owner with no tasks returns an empty plan without crashing; a required task is always scheduled even when it alone exceeds the time budget. Important because these are failure modes a real user would hit immediately.

**b. Confidence**

**★★★★☆** — The core behaviors (scheduling, sorting, filtering, recurrence, conflict detection) are all verified with both happy-path and edge-case tests. Confidence is not five stars because the following edge cases remain untested:

- A `start_time` string in an invalid format (e.g. `"8:00"` or `"25:99"`) would cause `_time_to_minutes` to raise an unhandled error.
- Filtering with both `pet_name` and `completed` combined has not been tested.
- An owner with zero pets (no `add_pet` calls) has not been tested through `generate_plan`.
- Behavior when two tasks share the same `task_id` is undefined and untested.

---

## 5. Reflection

**a. What went well**

The separation between the logic layer (`pawpal_system.py`) and the UI layer (`app.py`) worked cleanly. Because all scheduling logic lived in Python classes with no Streamlit dependencies, it was straightforward to test the scheduler in isolation using pytest without spinning up a browser. When Phase 3 features (sorting, conflict detection, recurrence) were added to the scheduler, they could be verified with tests before ever touching the UI. This separation also made the Streamlit code easier to read — `app.py` is mostly forms and display calls, not business logic.

**b. What you would improve**

The `task_id` field is currently a caller-constructed string (e.g. `"biscuit-morning-walk-0"`), which makes uniqueness dependent on naming discipline. In a second iteration, `task_id` would be auto-generated using `uuid.uuid4()` on construction so callers never have to think about it. I would also add a time-format validator to `Task` so that a malformed `start_time` like `"8:00"` fails loudly at creation time rather than crashing silently inside `_time_to_minutes` during sorting or conflict detection.

**c. Key takeaway**

The most important thing learned was that AI is most useful as a **critic and enumerator**, not an author. When asked "write me a scheduler," the AI produces plausible-looking code that may have subtle design flaws. When asked "what relationships or responsibilities are wrong in this design?" or "what edge cases would break this function?", the AI surfaces problems that are easy to miss when you're close to the code. The human's job is not to accept or reject whole suggestions, but to understand each piece well enough to evaluate it — and then integrate only the parts that fit the actual design. Being the "lead architect" means owning every decision even when the AI wrote the first draft.
