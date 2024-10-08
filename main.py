import click
import uvicorn
from rich.console import Console
from rich.table import Table
from pert_model_cal.interface.cli.cli_handler import CLIHandler
from pert_model_cal.server import app


@click.group()
def cli():
    """Main CLI Group"""
    pass


@click.command("calculate")
@click.argument("json_path", type=click.Path(exists=True))
@click.option("--save-graph", is_flag=True, default=False, help="Show the PERT diagram")
@click.option(
    "--show-table", is_flag=True, default=False, help="Show the task table and summary"
)
@click.option(
    "--table-format",
    type=click.STRING,
    help="Output format of the table (comma-separated list of formats, e.g., 'csv,excel')",
)
@click.option(
    "--probability",
    type=int,
    default=None,
    help="Calculate the probability of finishing tasks less than the expected time",
)
def calculate(json_path, save_graph, show_table, table_format, probability):
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
    config_table.add_row("Save Graph", str(save_graph))
    config_table.add_row("Show Table", str(show_table))
    config_table.add_row("Table Format", table_format)
    if probability:
        config_table.add_row("Probability less than", str(probability))

    console.print(config_table)
    table_formats = table_format.split(",") if table_format else ["csv"]

    CLIHandler.init(
        json_path=json_path,
        save_graph=save_graph,
        show_table=show_table,
        table_format=table_formats,
    )
    CLIHandler.calculate_pert(time=probability)

    if show_table:
        console.print("Generating Table...")
        CLIHandler.generate_table()

    if save_graph:
        console.print("Generating Graph...")
        CLIHandler.generate_graph_svg()


@click.command("start-server")
@click.option("--host", default="127.0.0.1", help="Host to run server on")
@click.option("--port", default=8080, help="Port to run server on")
def start_server(host, port):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli.add_command(calculate)
    cli.add_command(start_server)
    cli()
