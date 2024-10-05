from pydantic import BaseModel, Field, model_validator


class TaskInput(BaseModel):
    label: str
    name: str | None
    optimistic_estimate: int | float = Field(
        ..., gt=0, description="Optimistic time of a task, must be a positive"
    )
    most_likely_estimate: int | float = Field(
        ..., gt=0, description="Most likely time of a task, must be a positive"
    )
    pessimistic_estimate: int | float = Field(
        ..., gt=0, description="Pessimistic time of a task, must be a positive"
    )
    predecessors: list[str] | None = Field(
        default=[], description="Predecessors of a task"
    )

    @model_validator(mode="before")
    def check_predecessors(cls, values: dict) -> dict:
        label = values.get("label")
        predecessors = values.get("predecessors", [])

        # Check if the task is its own predecessor
        if label in predecessors:
            raise ValueError(f"Task '{label}' cannot be its own predecessor.")

        return values
