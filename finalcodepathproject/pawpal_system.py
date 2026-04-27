from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class Task:
    description: str
    time: str
    frequency: str = "once"
    completed: bool = False
    pet_name: str = ""
    due_date: Optional[str] = None

    def __post_init__(self):
        if self.due_date is None:
            self.due_date = datetime.now().strftime("%Y-%m-%d")

    def mark_complete(self):
        self.completed = True

    def next_occurrence(self):
        if self.frequency not in ("daily", "weekly"):
            return None
        base = datetime.strptime(self.due_date, "%Y-%m-%d")
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(days=7)
        nxt = base + delta
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            completed=False,
            pet_name=self.pet_name,
            due_date=nxt.strftime("%Y-%m-%d"),
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        task.pet_name = self.name
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def all_tasks(self) -> List[Task]:
        out = []
        for pet in self.pets:
            out.extend(pet.tasks)
        return out


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_by_time(self) -> List[Task]:
        return sorted(self.owner.all_tasks(), key=lambda t: t.time)

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        return [t for t in self.owner.all_tasks() if t.pet_name == pet_name]

    def filter_by_status(self, completed: bool) -> List[Task]:
        return [t for t in self.owner.all_tasks() if t.completed == completed]

    def detect_conflicts(self) -> List[str]:
        warnings = []
        tasks = self.owner.all_tasks()
        for i, a in enumerate(tasks):
            for b in tasks[i + 1:]:
                if a.time == b.time and a.due_date == b.due_date:
                    warnings.append(
                        f"Conflict at {a.time} on {a.due_date}: "
                        f"{a.pet_name}/{a.description} vs {b.pet_name}/{b.description}"
                    )
        return warnings

    def mark_task_complete(self, pet_name: str, description: str):
        for pet in self.owner.pets:
            if pet.name != pet_name:
                continue
            for task in pet.tasks:
                if task.description == description and not task.completed:
                    task.mark_complete()
                    nxt = task.next_occurrence()
                    if nxt is not None:
                        pet.add_task(nxt)
                    return True
        return False

    def todays_schedule(self) -> List[Task]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [t for t in self.sort_by_time() if t.due_date == today]
