import json
import logging
from pydantic import ValidationError

from .model.input import TaskInput
from .model.task_data import Task

logger = logging.getLogger(__name__)


class InputParser:

    @staticmethod
    def load_json_file(file_path: str) -> list[Task] | None:
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                logger.info(f"Loaded json file: {file_path}")
                task_list: list[Task] = []

                for raw_task_input in data:
                    try:
                        task_input = TaskInput(**raw_task_input)
                        task = Task(task_input)
                        task_list.append(task)
                    except ValidationError as e:
                        logger.error(f"Json file is invalid: {file_path}, {e}")
                        return None

                logger.info(f"Json file is valid: {file_path}")
                return task_list

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Json file is invalid: {file_path}, {e}")
            return None

        except ValueError as ve:
            logger.error(f"ValueError while processing file: {file_path}, {ve}")
            return None
