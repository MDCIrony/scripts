import typer
from .main import app as ty


app = typer.Typer()


app.add_typer(ty, name="query")

