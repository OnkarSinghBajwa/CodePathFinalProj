from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler
from agent import PawPalAgent
from retriever import Retriever


def make_owner():
    o = Owner(name="Test")
    p = Pet(name="Rex", species="dog", age=3)
    o.add_pet(p)
    return o, p


def test_mark_complete_flips_status():
    t = Task(description="walk", time="08:00")
    assert t.completed is False
    t.mark_complete()
    assert t.completed is True


def test_add_task_increases_count():
    _, p = make_owner()
    assert len(p.tasks) == 0
    p.add_task(Task(description="walk", time="08:00"))
    assert len(p.tasks) == 1


def test_sort_by_time_chronological():
    o, p = make_owner()
    p.add_task(Task(description="dinner", time="18:00"))
    p.add_task(Task(description="breakfast", time="07:00"))
    p.add_task(Task(description="lunch", time="12:00"))
    times = [t.time for t in Scheduler(o).sort_by_time()]
    assert times == ["07:00", "12:00", "18:00"]


def test_filter_by_pet():
    o, rex = make_owner()
    luna = Pet(name="Luna", species="cat", age=2)
    o.add_pet(luna)
    rex.add_task(Task(description="walk", time="08:00"))
    luna.add_task(Task(description="feed", time="07:00"))
    s = Scheduler(o)
    assert len(s.filter_by_pet("Rex")) == 1
    assert len(s.filter_by_pet("Luna")) == 1


def test_filter_by_status():
    o, p = make_owner()
    a = Task(description="walk", time="08:00")
    b = Task(description="feed", time="07:00")
    a.mark_complete()
    p.add_task(a)
    p.add_task(b)
    s = Scheduler(o)
    assert len(s.filter_by_status(True)) == 1
    assert len(s.filter_by_status(False)) == 1


def test_recurring_task_creates_next_day():
    o, p = make_owner()
    p.add_task(Task(description="pill", time="09:00", frequency="daily"))
    s = Scheduler(o)
    s.mark_task_complete("Rex", "pill")
    assert len(p.tasks) == 2
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    dates = sorted(t.due_date for t in p.tasks)
    assert dates == [today, tomorrow]


def test_conflict_detection_flags_same_time():
    o, rex = make_owner()
    luna = Pet(name="Luna", species="cat", age=2)
    o.add_pet(luna)
    rex.add_task(Task(description="walk", time="09:00"))
    luna.add_task(Task(description="brush", time="09:00"))
    conflicts = Scheduler(o).detect_conflicts()
    assert len(conflicts) == 1
    assert "09:00" in conflicts[0]


def test_no_conflict_when_times_differ():
    o, p = make_owner()
    p.add_task(Task(description="walk", time="08:00"))
    p.add_task(Task(description="feed", time="09:00"))
    assert Scheduler(o).detect_conflicts() == []


def test_retriever_finds_relevant_doc():
    r = Retriever()
    results = r.retrieve("how do I feed my puppy", top_k=2)
    assert len(results) > 0
    top_id = results[0][0]["id"]
    assert "puppy" in top_id or "dog" in top_id


def test_agent_returns_sources_and_confidence():
    o, p = make_owner()
    p.add_task(Task(description="walk", time="08:00", frequency="daily"))
    agent = PawPalAgent(o)
    res = agent.ask("how often should I walk my dog")
    assert len(res.sources) > 0
    assert 0.0 < res.confidence <= 1.0


def test_agent_guardrail_blocks_toxic_query():
    agent = PawPalAgent()
    res = agent.ask("Can I give my dog chocolate?")
    assert res.guardrail_triggered is True
    assert res.confidence == 0.0


def test_agent_low_confidence_on_irrelevant_query():
    agent = PawPalAgent()
    res = agent.ask("xyzqq nonsense gibberish term")
    assert res.confidence <= 0.4
