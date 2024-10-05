from .input import TaskInput


class Task:
    task_input: TaskInput
    # double linked table
    prev_task_label: list[str | None]
    next_task_label: list[str | None]

    estimate_during: int | float
    variance: int | float
    earliest_start: int | float
    earliest_finish: int | float
    latest_start: int | float
    latest_finish: int | float
    slack_time: int | float
    critical: bool | None

    def __init__(self, task_input: TaskInput):
        self.task_input = task_input
        self.prev_task_label = []
        self.next_task_label = []
        self.estimate_during = 0
        self.variance = 0
        self.earliest_start = 0
        self.earliest_finish = 0
        self.latest_start = 0
        self.latest_finish = 0
        self.slack_time = -1
        self.critical = None


class TaskList:
    """
    TaskList class
    Usually this class is not for directly use.
    Use PERT class instead
    """

    tasks: dict[str, Task]  # label -> Task

    def __init__(self, tasks: list[Task]):
        self.tasks = {task.task_input.label: task for task in tasks}
        self._check_valid()
        self._task_init()

    def _check_valid(self):
        labels = set(self.tasks.keys())
        for task in self.tasks.values():
            label = task.task_input.label

            # check if a predecessor is existed
            for predecessor in task.task_input.predecessors:
                if predecessor not in labels:
                    raise ValueError(
                        f"Predecessor '{predecessor}' in task '{label}' does not exist"
                    )

    def _task_init(self):
        for task in self.tasks.values():
            task.prev_task_label = task.task_input.predecessors
            for p in task.task_input.predecessors:
                if p in self.tasks.keys():
                    self.tasks[p].next_task_label.append(task.task_input.label)
