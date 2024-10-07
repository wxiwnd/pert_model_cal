import logging
from pathlib import Path
from ...core.model.output import PERTResult
from ...core.pert_calculator import PERT
from ..functions import IOUtils

logger = logging.getLogger(__name__)


class CLIHandler:
    pert: PERT
    pert_result: PERTResult
    show_diagram: bool
    show_table: bool
    table_format: str
    result_dir: Path

    @classmethod
    def init(
        cls,
        json_path: str,
        show_diagram: bool = True,
        show_table: bool = True,
        table_format="csv",
    ):
        cls.show_diagram = show_diagram
        cls.show_table = show_table
        cls.table_format = table_format
        task_list = IOUtils.load_tasks_from_json(json_path)
        cls.pert = PERT(tasks=task_list)
        cls.result_dir = IOUtils.create_dir("result")

    @classmethod
    def calculate_pert(cls, time: int | float | None):
        cls.pert_result = cls.pert.calculate_pert(time)

    @classmethod
    def generate_table(cls):
        """
        Generate a table and print
        cls.calculate_pert is needed
        """
        IOUtils.generate_table(
            pert_result=cls.pert_result,
            table_format=cls.table_format,
            show_table=cls.show_table,
            save_path=cls.result_dir,
        )

    @classmethod
    def generate_diagram(cls):
        raise NotImplementedError("Diagram is not implemented yet")
