import logging
import os
import pandas as pd

from rich.console import Console
from rich.table import Table
from ...core.model.output import PERTResult
from ...core.input_parser import InputParser
from ...core.pert_calculator import PERT

logger = logging.getLogger(__name__)


class CLIHandler:
    pert: PERT
    pert_result: PERTResult
    show_diagram: bool
    show_table: bool
    table_format: str
    result_dir: str

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
        task_list = InputParser.load_json_file(json_path)
        if task_list:
            cls.pert = PERT(tasks=task_list)
        else:
            logger.error("Load PERT calculator failed, please check your input.")

        cls.result_dir = os.path.join(os.getcwd(), "result")
        os.makedirs(cls.result_dir, exist_ok=True)

    @classmethod
    def calculate_pert(cls, time: int | float | None):
        cls.pert_result = cls.pert.calculate_pert(time)

    @classmethod
    def generate_table(cls):
        tasks_data = []
        for task in cls.pert_result.tasks:
            tasks_data.append(
                {
                    "Label": task.label,
                    "Earliest Start": task.earliest_start,
                    "Earliest Finish": task.earliest_finish,
                    "Latest Start": task.latest_start,
                    "Latest Finish": task.latest_finish,
                    "Slack": task.slack_time,
                    "Critical": task.critical,
                }
            )
        tasks_df = pd.DataFrame(tasks_data)

        summary_data = {
            "Critical Path": [", ".join(cls.pert_result.critical_path)],
            "Expected Duration": [cls.pert_result.expected_duration],
            "Expected Probability": [cls.pert_result.expected_probability],
        }
        summary_df = pd.DataFrame(summary_data)

        # save the file
        if cls.table_format == "csv":
            tasks_save_path = os.path.join(cls.result_dir, "tasks.csv")
            summary_save_path = os.path.join(cls.result_dir, "summary.csv")
            tasks_df.to_csv(tasks_save_path, index=False)
            summary_df.to_csv(summary_save_path, index=False)

        elif cls.table_format == "excel":
            tasks_save_path = os.path.join(cls.result_dir, "tasks.xlsx")
            summary_save_path = os.path.join(cls.result_dir, "summary.xlsx")
            tasks_df.to_excel(tasks_save_path, index=False)
            summary_df.to_excel(summary_save_path, index=False)

        if cls.show_table:
            console = Console()
            table = Table(show_header=True)

            for column in tasks_df.columns:
                table.add_column(column)
            for _, row in tasks_df.iterrows():
                table.add_row(*map(str, row))

            console.print(table)

    @classmethod
    def generate_diagram(cls):
        raise NotImplementedError("Diagram is not implemented yet")
