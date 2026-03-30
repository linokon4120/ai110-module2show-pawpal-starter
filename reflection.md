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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector checks for **exact time-window overlaps** (task A starts before task B ends, and task B starts before task A ends) but does not account for travel time, setup time, or owner fatigue between tasks. Two tasks scheduled back-to-back — one ending at 08:30 and the next starting at 08:30 — are considered non-conflicting even if the owner realistically needs a few minutes between them.

This tradeoff is reasonable for a first version because: (1) the exact overlap check covers the most obvious scheduling mistakes without requiring extra configuration; (2) adding buffer time would require the owner to specify it per task or globally, which adds friction for a daily-use tool; and (3) the scheduler's purpose is to help, not to perfectly simulate reality — a warning about an actual overlap is more useful than false positives from a buffer that may not apply to every task pair.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
