import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — acts as the app's persistent memory across reruns.
# The Owner object (and all pets/tasks nested inside it) lives here so that
# clicking a button doesn't wipe everything out.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Section 1: Owner profile
# ---------------------------------------------------------------------------
st.header("Owner Profile")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Your name", value="Alex")
    with col2:
        available_minutes = st.number_input(
            "Daily care time (minutes)", min_value=10, max_value=480, value=90
        )
    save_owner = st.form_submit_button("Save Profile")

if save_owner:
    # Preserve pets that were already added under the previous owner object
    existing_pets = st.session_state.owner.pets if st.session_state.owner else []
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    st.session_state.owner.pets = existing_pets
    st.success(f"Profile saved — {owner_name}, {available_minutes} min/day.")

if st.session_state.owner is None:
    st.info("Fill in your profile above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 2: Pets
# ---------------------------------------------------------------------------
st.divider()
st.header("Pets")

with st.form("add_pet_form"):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
    with col2:
        age = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=1.0, step=0.5)
        notes = st.text_input("Special notes (optional)")
    add_pet = st.form_submit_button("Add Pet")

if add_pet:
    if pet_name.strip():
        owner.add_pet(Pet(name=pet_name.strip(), species=species, age=age, notes=notes))
        st.success(f"{pet_name.strip()} added!")
    else:
        st.error("Pet name cannot be empty.")

if owner.pets:
    for pet in owner.pets:
        label = f"**{pet.name}** — {pet.species}, {pet.age} yrs"
        if pet.notes:
            label += f" _(_{pet.notes}_)_"
        st.markdown(label + f" &nbsp; `{len(pet.tasks)} task(s)`")
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3: Tasks
# ---------------------------------------------------------------------------
st.divider()
st.header("Tasks")

if not owner.pets:
    st.info("Add a pet before adding tasks.")
else:
    with st.form("add_task_form"):
        pet_options = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Add task to", pet_options)

        col1, col2 = st.columns(2)
        with col1:
            task_name = st.text_input("Task name", value="Morning walk")
            category = st.selectbox(
                "Category", ["walk", "feeding", "medication", "grooming", "enrichment", "other"]
            )
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority_label = st.selectbox("Priority", ["1 — High", "2 — Medium", "3 — Low"])

        is_required = st.checkbox("Required (always include in plan)")
        add_task = st.form_submit_button("Add Task")

    if add_task:
        if task_name.strip():
            target_pet = owner.get_pet(selected_pet_name)
            priority_val = int(priority_label[0])
            # Build a unique task_id from pet name + task name + current task count
            task_id = f"{selected_pet_name}-{task_name.strip().lower().replace(' ', '-')}-{len(target_pet.tasks)}"
            target_pet.add_task(Task(
                name=task_name.strip(),
                category=category,
                duration_minutes=int(duration),
                priority=priority_val,
                is_required=is_required,
                task_id=task_id,
            ))
            st.success(f"'{task_name.strip()}' added to {selected_pet_name}.")
        else:
            st.error("Task name cannot be empty.")

    # Display each pet's task list
    for pet in owner.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks**")
            for task in pet.tasks:
                req_badge = " 🔴 required" if task.is_required else ""
                st.markdown(
                    f"- `{task.category}` &nbsp; {task.name} — {task.duration_minutes} min, "
                    f"priority {task.priority}{req_badge}"
                )

# ---------------------------------------------------------------------------
# Section 4: Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.header("Today's Schedule")

if st.button("Generate Plan", type="primary"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a plan.")
    else:
        scheduler = Scheduler(owner=owner)
        plan = scheduler.generate_plan()
        st.code(plan.summary(), language=None)

        if plan.skipped_tasks:
            st.caption(
                f"{len(plan.skipped_tasks)} task(s) skipped. "
                "Increase daily care time or lower task durations to fit them in."
            )

        with st.expander("Show reasoning"):
            for reason in plan.reasoning:
                st.markdown(f"- {reason}")
