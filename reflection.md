# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Three core user actions:**

1. **Enter owner and pet info** — The user can provide basic details about themselves and their pet (like owner name, pet name and species, and total time available for care each day).

2. **Add and manage care tasks** — The user creates individual care tasks (walks, feeding, medication, grooming, enrichment, etc.), each with at minimum a name, estimated duration, and priority level. The user should also be able to edit or remove tasks so the list stays accurate over time.

3. **Generate and view the daily plan** — The user triggers the scheduler, which takes the task list and owner constraints, selects and orders tasks that fit within the available time window, and displays the resulting daily schedule. Ideally the app also explains why certain tasks were included or excluded (e.g., "Medication was scheduled first because it is high priority; enrichment walk was skipped because no time remained").

**Classes, attributes, and methods:**

**`Owner`**
- Attributes: `name` (str), `available_minutes` (int — total care time per day)
- Methods:
  - `has_time_for(task)` → bool — checks whether a task fits within remaining availability
  - `__repr__` — human-readable summary for display

**`Pet`**
- Attributes: `name` (str), `species` (str), `age` (int/float), `notes` (str — any special needs or preferences)
- Methods:
  - `__repr__` — human-readable summary for display

**`Task`**
- Attributes: `name` (str), `category` (str — e.g. walk, feeding, medication, grooming), `duration_minutes` (int), `priority` (int or enum — e.g. 1=high, 2=medium, 3=low), `is_required` (bool — e.g. medication is non-negotiable)
- Methods:
  - `is_higher_priority_than(other)` → bool — comparison helper for sorting
  - `__repr__` — human-readable summary for display

**`Scheduler`**
- Attributes: `owner` (Owner), `pet` (Pet), `tasks` (list[Task])
- Methods:
  - `add_task(task)` — adds a task to the list
  - `remove_task(name)` — removes a task by name
  - `generate_plan()` → DailyPlan — sorts tasks by priority, fits them within available time, returns a plan with reasoning

**`DailyPlan`**
- Attributes: `scheduled_tasks` (list[Task] — tasks that made the cut), `skipped_tasks` (list[Task] — tasks that were dropped and why), `reasoning` (list[str] — one explanation per scheduling decision)
- Methods:
  - `summary()` → str — formats the full plan as a readable string for display in the UI

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
