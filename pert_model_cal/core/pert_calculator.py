import scipy
import math

import scipy.stats

from .model.task_data import Task, TaskList
from .model.output import PERTResult, TaskOut


class PERT(TaskList):
    critical_path: list[str]
    expected_time: int | float | None
    expected_probability: int | float | None

    def __init__(self, tasks: list[Task]):
        super().__init__(tasks)
        self.critical_path = []
        self.expected_time = None
        self.expected_probability = None

        for task in self.tasks.values():
            task.estimate_during = (
                task.task_input.optimistic_estimate
                + 4 * task.task_input.most_likely_estimate
                + task.task_input.pessimistic_estimate
            ) / 6
            task.variance = (
                (
                    task.task_input.pessimistic_estimate
                    - task.task_input.optimistic_estimate
                )
                / 6
            ) ** 2

    def _earliest_time(self):
        for task in self.tasks.values():
            if not task.prev_task_label:
                task.earliest_finish = task.estimate_during

        for task in self.tasks.values():
            for next_task in task.next_task_label:
                if self.tasks[next_task].earliest_start < task.earliest_finish:
                    self.tasks[next_task].earliest_start = task.earliest_finish
                self.tasks[next_task].earliest_finish = (
                    self.tasks[next_task].earliest_start
                    + self.tasks[next_task].estimate_during
                )

    def _latest_time(self):
        during_time = 0
        for task in reversed(self.tasks.values()):
            if not task.next_task_label:
                during_time = max(during_time, task.earliest_finish)
                task.latest_finish = during_time
                task.latest_start = task.latest_finish - task.estimate_during

        for task in reversed(self.tasks.values()):
            for prev_task in task.prev_task_label:
                if (
                    self.tasks[prev_task].latest_finish == 0
                    or self.tasks[prev_task].latest_finish > task.latest_start
                ):
                    self.tasks[prev_task].latest_finish = task.latest_start

                self.tasks[prev_task].latest_start = (
                    self.tasks[prev_task].latest_finish
                    - self.tasks[prev_task].estimate_during
                )

    def _slack_time(self):
        for task in self.tasks.values():
            task.slack_time = task.latest_start - task.earliest_start

    def _critical(self):
        for task in self.tasks.values():
            task.critical = True if task.slack_time == 0 else False

    def _critical_path(self):
        for task in self.tasks.values():
            if task.critical:
                self.critical_path.append(task.task_input.label)

    def _expected_time(self):
        last_task = next(reversed(self.tasks.values()))
        self.expected_time = last_task.latest_finish

    def _probability(self, time: int | float):
        sum_v: float | int = 0
        for task in self.tasks.values():
            sum_v += task.variance if task.critical else 0
        std_dev = math.sqrt(sum_v)
        assert self.expected_time is not None
        z = (time - self.expected_time) / std_dev
        self.expected_probability = scipy.stats.norm.cdf(z)

    def calculate_pert(self, time: int | float | None = None) -> PERTResult:
        self._earliest_time()
        self._latest_time()
        self._slack_time()
        self._critical()
        self._expected_time()
        if time:
            self._probability(time=time)
        self._critical_path()

        return PERTResult(
            tasks=[TaskOut.from_task(task) for task in self.tasks.values()],
            critical_path=self.critical_path,
            expected_duration=self.expected_time,
            expected_probability=self.expected_probability,
        )
