import typer

from .codecommit import app as codecommit_app

app = typer.Typer()

app.add_typer(codecommit_app, name="codecommit")
