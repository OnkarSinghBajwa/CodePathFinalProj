import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler
from agent import PawPalAgent

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Me")
if "agent" not in st.session_state:
    st.session_state.agent = PawPalAgent(st.session_state.owner)

owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title("🐾 PawPal+")
st.caption("Smart pet care management with an AI advisor")

with st.sidebar:
    st.header("Add a pet")
    with st.form("add_pet", clear_on_submit=True):
        pname = st.text_input("Name")
        pspecies = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        page = st.number_input("Age", min_value=0, max_value=30, value=1)
        if st.form_submit_button("Add pet") and pname:
            owner.add_pet(Pet(name=pname, species=pspecies, age=int(page)))
            st.success(f"Added {pname}")

    st.header("Add a task")
    if owner.pets:
        with st.form("add_task", clear_on_submit=True):
            target = st.selectbox("Pet", [p.name for p in owner.pets])
            desc = st.text_input("Description")
            time_str = st.text_input("Time (HH:MM)", value="09:00")
            freq = st.selectbox("Frequency", ["once", "daily", "weekly"])
            if st.form_submit_button("Add task") and desc:
                for pet in owner.pets:
                    if pet.name == target:
                        pet.add_task(Task(description=desc, time=time_str, frequency=freq))
                        st.success(f"Added task for {target}")
                        break
    else:
        st.info("Add a pet first")

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Today's schedule")
    today = scheduler.todays_schedule()
    if not today:
        st.info("No tasks scheduled for today")
    else:
        for t in today:
            label = f"{t.time} — {t.pet_name}: {t.description} ({t.frequency})"
            cols = st.columns([4, 1])
            cols[0].write(("✅ " if t.completed else "⬜ ") + label)
            if not t.completed:
                if cols[1].button("Done", key=f"{t.pet_name}-{t.description}-{t.time}"):
                    scheduler.mark_task_complete(t.pet_name, t.description)
                    st.rerun()

    st.subheader("Conflicts")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for c in conflicts:
            st.warning(c)
    else:
        st.success("No scheduling conflicts")

with col2:
    st.subheader("Ask the PawPal advisor")
    query = st.text_input("Question", placeholder="e.g. how often should I walk my dog?")
    if st.button("Ask") and query:
        result = st.session_state.agent.ask(query)
        if result.guardrail_triggered:
            st.error(result.answer)
        else:
            st.markdown(result.answer)
            st.caption(
                f"Plan: {' → '.join(result.plan)} | "
                f"Sources: {result.sources} | "
                f"Confidence: {result.confidence}"
            )
