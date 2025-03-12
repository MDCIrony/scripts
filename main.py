import typer

from aws import app as aws_app

app = typer.Typer()


app.add_typer(aws_app, name="aws")


if __name__ == "__main__":
    app()
