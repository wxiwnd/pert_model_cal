import pandas as pd
from ..core.model.task_data import Task
from rich.console import Console
from rich.table import Table
from pathlib import Path
from ..core.input_parser import InputParser
from ..core.model.output import PERTResult


class IOUtils:
    """
    Contain functions with io operations
    """

    @staticmethod
    def load_tasks_from_json(file_location: Path | str) -> list[Task]:
        if not isinstance(file_location, Path):
            file_location = Path(file_location)
        tasks = InputParser.load_json_file(file_location)
        if tasks is None:
            raise ValueError("Invalid JSON file")
        return tasks

    @staticmethod
    def create_dir(dir_name: str) -> Path:
        result_dir = Path.cwd() / dir_name
        if not result_dir.exists():
            result_dir.mkdir(parents=True, exist_ok=True)
        return result_dir

    @staticmethod
    def generate_table(
        pert_result: PERTResult, table_format: str, show_table: bool, save_path: Path
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        tasks_data = []
        for task in pert_result.tasks:
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
            "Critical Path": [", ".join(pert_result.critical_path)],
            "Expected Duration": [pert_result.expected_duration],
            "Expected Probability": [pert_result.expected_probability],
        }
        summary_df = pd.DataFrame(summary_data)

        # save the file
        if table_format == "csv":
            tasks_save_path = save_path / "tasks.csv"
            summary_save_path = save_path / "summary.csv"
            tasks_df.to_csv(tasks_save_path, index=False)
            summary_df.to_csv(summary_save_path, index=False)

        elif table_format == "excel":
            tasks_save_path = save_path / "tasks.xlsx"
            summary_save_path = save_path / "summary.xlsx"
            tasks_df.to_excel(tasks_save_path, index=False)
            summary_df.to_excel(summary_save_path, index=False)

        if show_table:
            console = Console()
            tasks_table = Table(show_header=True)

            for column in tasks_df.columns:
                tasks_table.add_column(column)
            for _, row in tasks_df.iterrows():
                tasks_table.add_row(*map(str, row))

            summary_table = Table(show_header=True)

            for column in summary_df.columns:
                summary_table.add_column(column)
            for _, row in summary_df.iterrows():
                summary_table.add_row(*map(str, row))

            console.print(tasks_table)
            console.print(summary_table)

        return (tasks_df, summary_df)
