from typing import Annotated
from urllib import request as client
import typer
from bs4 import BeautifulSoup
from http.client import HTTPResponse
from rich import print

app = typer.Typer()

@app.command()
def goal(
        level: Annotated[str, typer.Argument()],
) -> None:

    request = client.Request(f"https://overthewire.org/wargames/bandit/bandit{level}.html", method="GET")
    response: HTTPResponse = client.urlopen(request)

    site = response.read().decode("utf-8")

    if site:
        soup = BeautifulSoup(site, features="html.parser")
        target_tag = soup.find(name="h2", id="level-goal")

        if target_tag:
            goal = target_tag.find_next("p")
        if goal:
            tip = goal.find_next("p")

    if goal: print(f"Goal: {goal.text}.")

    if tip:
        text_list = tip.text.split(sep=",")
        text_list_parsed = [command.split() for command in text_list]
        print(f"Tips: {text_list_parsed}")
# Verificar si el comando fue exitoso
    # if result.returncode == 0:
    #     html_content = result.stdout  # Guardar el HTML
    #     soup = BeautifulSoup(html_content, "ml.parser")  # Parsear con BeautifulSoup
    #
    #     # Buscar una etiqueta específica (ejemplo: <h2>)
    #     target_tag = soup.find("h2")  # Busca la primera etiqueta <h2>
    #     
    #     if target_tag:
    #         print("Texto dentro de la etiqueta:", target_tag.text)
    #     else:
    #         print("Etiqueta no encontrada")
    # else:
    #     print("Fallo algo")
        
