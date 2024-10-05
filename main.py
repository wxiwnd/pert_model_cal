import click
from rich.console import Console
from rich.table import Table
from pert_model_cal.interface.cli.cli_handler import CLIHandler


@click.command()
@click.argument("json_path", type=click.Path(exists=True))
@click.option(
    "--show-diagram", is_flag=True, default=False, help="Show the PERT diagram"
)
@click.option(
    "--show-table", is_flag=True, default=True, help="Show the task table and summary"
)
@click.option(
    "--table-format",
    type=click.Choice(["csv", "excel"]),
    default="csv",
    help="Output format of the table (csv or excel)",
)
@click.option(
    "--probability",
    type=int,
    default=None,
    help="Calculate the probability of finishing tasks less than the expected time",
)
def main(json_path, show_diagram, show_table, table_format, probability):
    """
    CLI to handle PERT calculations.
    """
    console = Console()
    config_table = Table(
        title="Configuration", show_header=True, header_style="bold cyan"
    )
    config_table.add_column("Option", justify="right", style="cyan", no_wrap=True)
    config_table.add_column("Value", justify="left", style="magenta")

    config_table.add_row("Processing File", json_path)
    config_table.add_row("Show Diagram", str(show_diagram))
    config_table.add_row("Show Table", str(show_table))
    config_table.add_row("Table Format", table_format)
    if probability:
        config_table.add_row("Probability less than", str(probability))

    console.print(config_table)

    CLIHandler.init(
        json_path=json_path,
        show_diagram=show_diagram,
        show_table=show_table,
        table_format=table_format,
    )
    CLIHandler.calculate_pert(time=probability)

    if show_table:
        console.print("Generating table...")
        CLIHandler.generate_table()

    if show_diagram:
        click.echo("Generating diagram...")
        try:
            CLIHandler.generate_diagram()
        except NotImplementedError:
            click.echo("Diagram generation is not yet implemented.")


if __name__ == "__main__":
    main()
