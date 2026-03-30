# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- **Owner & multi-pet profile** — Set your name, daily care budget (minutes), and register any number of pets with species, age, and notes.
- **Task management** — Add tasks per pet with name, category, duration, priority, start time, and recurrence frequency.
- **Priority scheduling** — Required tasks are always scheduled first; optional tasks are sorted by priority level, then duration to maximise what fits within the daily budget.
- **Sorting by time** — All tasks across all pets are displayed in a single chronological table sorted by `HH:MM` start time; unscheduled tasks appear at the bottom.
- **Conflict warnings** — The scheduler checks each pet's scheduled tasks for overlapping time windows and surfaces a plain-English `⚠` warning before generating the plan.
- **Recurring tasks** — Mark a daily or weekly task complete and a new instance is automatically created with the due date shifted by one day or seven days respectively.
- **Filtering** — Query tasks by pet name, completion status, or both using `Scheduler.filter_tasks()`.
- **Reasoning log** — Every scheduling decision (why a task was included or skipped) is recorded and available via an expandable panel in the UI.

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

> On macOS without a virtual environment, use `python3 -m pytest` instead.

**19 tests** across 6 areas:

| Area | What is verified |
|---|---|
| Task completion | `mark_complete()` flips `completed` to `True` |
| Pet task count | `add_task()` increases the pet's task list by one |
| Sorting | Tasks come back in chronological `HH:MM` order; unscheduled tasks go last |
| Recurring tasks | Daily → next due +1 day; weekly → +7 days; non-recurring → `None` returned; original marked done |
| Conflict detection | Overlapping windows flagged; adjacent tasks and cross-pet overlaps are not |
| Filtering & edge cases | `filter_tasks` by pet/status; empty-task owners don't crash; required tasks scheduled even over budget |

**Confidence: 4/5 stars ** — core scheduling logic, sorting, filtering, recurrence, and conflict detection are all covered. Edge cases not yet tested: tasks with missing/malformed `start_time` values, an owner with zero pets, and filtering with both `pet_name` and `completed` combined.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

The scheduler goes beyond a simple priority list with four additional capabilities:

- **Sorting by time** — `Scheduler.sort_tasks_by_time()` returns all tasks ordered by their `start_time` (`HH:MM`), with unscheduled tasks appended at the end.
- **Filtering** — `Scheduler.filter_tasks(pet_name=..., completed=...)` returns tasks matching any combination of pet and completion status.
- **Recurring tasks** — Tasks carry a `frequency` field (`"none"` / `"daily"` / `"weekly"`). Calling `Scheduler.mark_task_complete(task_id)` marks the task done and automatically adds the next occurrence (due date shifted by `timedelta`) to the same pet.
- **Conflict detection** — `Scheduler.detect_conflicts()` scans each pet's scheduled tasks and returns a warning string for any pair whose time windows overlap.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
