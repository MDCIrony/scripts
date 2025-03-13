import typer

from aws import app as aws_app
from otw import app as otw_app

app = typer.Typer()


app.add_typer(aws_app, name="aws")
app.add_typer(otw_app, name="otw")

if __name__ == "__main__":
    app()
