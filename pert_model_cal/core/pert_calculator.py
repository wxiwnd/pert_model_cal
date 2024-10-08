import scipy
import math
from typing import TypedDict
import queue
import scipy.stats
import networkx
from .model.task_data import Task, TaskList, GraphData
from .model.output import PERTResult, TaskOut


class PERT(TaskList):
    critical_path: list[str]
    expected_time: int | float | None
    expected_probability: int | float | None
    graph: networkx.DiGraph | None

    def __init__(self, tasks: list[Task]):
        super().__init__(tasks)
        self.critical_path = []
        self.expected_time = None
        self.expected_probability = None
        self.graph = None

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

    def _graph(self):
        # record position
        class Position(TypedDict):
            x: int
            y: int

        self.graph = networkx.DiGraph()
        buffer = queue.Queue()
        node_positions: dict[str, Position] = {}
        # param of networkx(tuple)
        position_map = {}
        x = 0

        for task in self.tasks.values():
            if task.critical:
                label = task.task_input.label
                buffer.put(label)
                self.graph.add_node(label)
                node_positions[label] = Position(x=x, y=0)
                position_map[label] = (x, 0)
                x += 3
                for prev_task in task.prev_task_label:
                    if prev_task in self.graph.nodes:
                        self.graph.add_edge(
                            self.tasks[prev_task].task_input.label,
                            task.task_input.label,
                            name=task.task_input.label,
                        )

        start = "#!start"  # a unique label in str
        self.graph.add_node(start)
        position_map[start] = (-3, 0)
        self.graph.add_edge(start, buffer.queue[0], name=buffer.queue[0])
        end = buffer.queue[-1]  # the last task in critical path

        dashed_edges = []
        while not buffer.empty():
            present = buffer.get()
            next_tasks = self.tasks[present].next_task_label
            next_task_count = len(next_tasks)

            if next_task_count > 1:
                task_range = math.floor(math.log2(next_task_count))
            elif next_task_count == 1:
                task_range = node_positions[present]["y"]
            if not next_tasks and present != end:
                self.graph.add_edge(present, end)
                continue

            for next_task in next_tasks:
                if next_task not in self.graph.nodes:
                    self.graph.add_node(next_task)
                    y = task_range
                    x = node_positions[present]["x"] * (1 - (y / 20.0)) + 2
                    node_positions[next_task] = Position(x=x, y=y)
                    position_map[next_task] = (x, y)
                    task_range -= 1

                    # tolerance
                    if task_range <= 0:
                        task_range -= 1
                    self.graph.add_edge(present, next_task, name=next_task)
                    buffer.put(next_task)
                else:
                    present_ef = self.tasks[present].earliest_finish
                    next_es = self.tasks[next_task].earliest_start
                    if present_ef > next_es:
                        predecessors = list(self.graph.predecessors(next_task))
                        for pred in predecessors:
                            self.graph.remove_edge(pred, next_task)
                            self.graph.add_edge(pred, next_task)
                            dashed_edges.append((pred, next_task))
                        self.graph.add_edge(present, next_task, name=next_task)
                    elif present_ef < next_es:
                        for prev_task in self.tasks[next_task].prev_task_label:
                            if self.tasks[prev_task].critical:
                                self.graph.add_edge(present, prev_task)
                                dashed_edges.append((present, prev_task))
                    else:
                        predecessors = list(self.graph.predecessors(next_task))
                        for pred in predecessors:
                            if (
                                self.tasks[pred].critical
                                and not self.tasks[present].critical
                            ):
                                self.graph.remove_edge(pred, next_task)
                                self.graph.add_edge(pred, next_task)
                                dashed_edges.append((pred, next_task))
                                # connect last tasks
                                self.graph.add_edge(present, next_task, name=next_task)

        dashed_edges = [(u, v) for u, v in self.graph.edges if (u, v) in dashed_edges]
        solid_edges = [
            (u, v) for u, v in self.graph.edges if (u, v) not in dashed_edges
        ]
        return GraphData(
            graph=self.graph,
            position_map=position_map,
            dashed_edges=dashed_edges,
            solid_edges=solid_edges,
        )

    def calculate_pert(self, time: int | float | None = None) -> PERTResult:
        self._earliest_time()
        self._latest_time()
        self._slack_time()
        self._critical()
        self._expected_time()
        if time:
            self._probability(time=time)
        self._critical_path()
        graph_data = self._graph()

        return PERTResult(
            tasks=[TaskOut.from_task(task) for task in self.tasks.values()],
            critical_path=self.critical_path,
            expected_duration=self.expected_time,
            expected_probability=self.expected_probability,
            graph_data=graph_data,
        )
