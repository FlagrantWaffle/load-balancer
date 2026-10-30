from rich.console import Console
from rich.table import Table

def create_server_health_table(server_info):

    console = Console()
    table = Table(title="Server Cluster Status")
    table.add_column("Server", style="cyan")
    table.add_column("Status", style="green")

    for server in server_info:
        name, status_value, status_phrase = server.values()
        colour_override = None

        if status_value >= 400:
            colour_override = "red"

        table.add_row(name, f"{status_value} {status_phrase}", style=colour_override)    


    print("")
    console.print(table)