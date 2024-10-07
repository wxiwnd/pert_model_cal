import pandas as pd
from ..core.model.task_data import Task
from rich.console import Console
from rich.table import Table
from pathlib import Path
from ..core.input_parser import InputParser
from ..core.model.output import PERTResult
from ..core.pert_calculator import PERT


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
        pert_result: PERTResult,
        table_format: list[str],
        save_path: Path,
        show_table: bool = False,
        config_name: str | None = None,
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
        if "csv" in table_format:
            tasks_save_path = save_path / (
                f"{config_name}_tasks.csv" if config_name else "task.csv"
            )
            summary_save_path = save_path / (
                f"{config_name}_summary.csv" if config_name else "summary.csv"
            )
            tasks_df.to_csv(tasks_save_path, index=False)
            summary_df.to_csv(summary_save_path, index=False)

        if "excel" in table_format:
            tasks_save_path = save_path / (
                f"{config_name}_tasks.xlsx" if config_name else "task.xlsx"
            )
            summary_save_path = save_path / (
                f"{config_name}_summary.xlsx" if config_name else "summary.xlsx"
            )
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

    @staticmethod
    def calculate_pert(
        config_name: Path | str, time: int | float | None = None
    ) -> PERTResult:
        result_dir = IOUtils.create_dir("cache")
        if not isinstance(config_name, Path):
            config_name = Path(config_name)
        file_location = result_dir / config_name
        if not file_location.exists():
            raise FileNotFoundError(f"Config file {config_name}.json not found")

        tasks = IOUtils.load_tasks_from_json(file_location)
        pert = PERT(tasks)
        return pert.calculate_pert(time=time)
