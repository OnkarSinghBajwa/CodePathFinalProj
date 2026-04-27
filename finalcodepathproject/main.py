from pawpal_system import Owner, Pet, Task, Scheduler
from agent import PawPalAgent


def build_demo_owner() -> Owner:
    owner = Owner(name="Ducci")
    rex = Pet(name="Rex", species="dog", age=4)
    luna = Pet(name="Luna", species="cat", age=2)
    rex.add_task(Task(description="Morning walk", time="08:00", frequency="daily"))
    rex.add_task(Task(description="Dinner", time="18:00", frequency="daily"))
    rex.add_task(Task(description="Heartworm pill", time="09:00", frequency="weekly"))
    luna.add_task(Task(description="Brush coat", time="09:00", frequency="weekly"))
    luna.add_task(Task(description="Wet food", time="07:30", frequency="daily"))
    owner.add_pet(rex)
    owner.add_pet(luna)
    return owner


def print_schedule(scheduler: Scheduler):
    print("\n=== Today's schedule ===")
    for t in scheduler.todays_schedule():
        flag = "done" if t.completed else "pending"
        print(f"  {t.time}  {t.pet_name:6s}  {t.description:20s}  [{flag}]")


def print_conflicts(scheduler: Scheduler):
    conflicts = scheduler.detect_conflicts()
    print("\n=== Conflicts ===")
    if not conflicts:
        print("  none")
    for c in conflicts:
        print("  ! " + c)


def run_agent_examples(agent: PawPalAgent):
    queries = [
        "What should I feed my adult dog?",
        "Any conflicts on my schedule today?",
        "Can I give Rex chocolate as a treat?",
    ]
    for q in queries:
        print("\n" + "=" * 60)
        print(f"USER: {q}")
        result = agent.ask(q)
        print(f"PLAN:    {' -> '.join(result.plan)}")
        print(f"ACTIONS: {result.actions}")
        print(f"SOURCES: {result.sources}")
        print(f"CONFIDENCE: {result.confidence}")
        print(f"GUARDRAIL: {result.guardrail_triggered}")
        print(f"ANSWER:\n{result.answer}")


if __name__ == "__main__":
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    print_schedule(scheduler)
    print_conflicts(scheduler)

    print("\n--- Marking Rex's morning walk complete ---")
    scheduler.mark_task_complete("Rex", "Morning walk")
    print(f"Rex now has {len(owner.pets[0].tasks)} tasks (recurring instance added)")

    agent = PawPalAgent(owner)
    run_agent_examples(agent)
