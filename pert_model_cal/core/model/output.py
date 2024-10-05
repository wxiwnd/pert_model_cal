from pydantic import BaseModel
from .task_data import Task


class TaskOut(BaseModel):
    label: str
    estimate_duration: int | float | None = None
    variance: int | float | None = None
    earliest_start: int | float | None = None
    earliest_finish: int | float | None = None
    latest_start: int | float | None = None
    latest_finish: int | float | None = None
    slack_time: int | float | None = None
    critical: bool | None = None

    @classmethod
    def from_task(cls, task: Task) -> "TaskOut":
        return cls(
            label=task.task_input.label,
            estimate_duration=task.estimate_during,
            variance=task.variance,
            earliest_start=task.earliest_start,
            earliest_finish=task.earliest_finish,
            latest_start=task.latest_start,
            latest_finish=task.latest_finish,
            slack_time=task.slack_time,
            critical=task.critical,
        )


class PERTResult(BaseModel):
    # the result of every task
    tasks: list[TaskOut]
    critical_path: list[str]
    expected_duration: int | float
    expected_probability: int | float | None
