import json
import logging
import os
from asyncio import start_server
from pathlib import Path
from typing import Annotated, List

import boto3
import typer
from boto3.session import Session
from botocore.exceptions import ClientError
from mypy_boto3_codecommit import CodeCommitClient
from rich import print

from utils.main import prompt_input

app = typer.Typer()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("personal-cli")

app_name = "personal-cli"
PERSONAL_AWS_CONFIG = {
    "config": None,
}
# def repository_exist(repo_name:str):
#     print("Here something")


@app.callback()
def check_config():
    try:
        app_dir = typer.get_app_dir(app_name)
        PERSONAL_AWS_CONFIG["config_path"] = app_dir
        config_path = Path(app_dir) / ".aws.conf"

        if not config_path.exists():
            print(f"[WARN] Config file not found: {config_path}")
            raise typer.Exit(code=1)

        print("Reading config...")
        with open(config_path, "r") as f:
            config_json = json.load(f)
       
        PERSONAL_AWS_CONFIG.update(config_json)
        print("Config loaded")

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON config: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        raise typer.Exit(code=1)

    try:
        session_profile = PERSONAL_AWS_CONFIG["AWS_PROFILE"]
    except KeyError as k:
        print("[bold red]ALERT![/bold red] Configure the config file first: Missing key", k)
        logger.debug("Key error problem with aws config: %r", k)
        raise typer.Exit(code=1)

    logger.debug("Building CodeCommit client using profile: %s", session_profile)
    session: Session = boto3.Session(profile_name=session_profile)
    client: CodeCommitClient = session.client("codecommit")
    PERSONAL_AWS_CONFIG.update({
        "session": session,
        "client": client
    })


@app.command()
def pr_create(
        # aws_profile: Annotated[str, typer.Argument(envvar="AWS_PROFILE")],
    ) -> None:
    logger.debug("Create PR Task initialized")

    try:
        repo = PERSONAL_AWS_CONFIG["DEFAULT_REPO"]
        session_profile = PERSONAL_AWS_CONFIG["AWS_PROFILE"]
    except KeyError as k:
        print(f"[bold red]ALERT![bold red] Configure the config file first: {k}")
        raise typer.Exit(code=1)

    session: Session = boto3.Session(profile_name=session_profile)
    client: CodeCommitClient = session.client("codecommit")
    
    source_branch = prompt_input(
        client.list_branches,
        params={"repositoryName": repo},
        msg="Source branch (press h to list [- for name filter])",
        logger=logger
    )
    
    destination_branch = prompt_input(
        client.list_branches,
        params={"repositoryName": repo},
        msg="Destination branch (press h to list [- for name filter])",
        logger=logger
    )
    
    title = typer.prompt("PR Title: ")
    description = typer.prompt("PR Description: ")

    try:
        
        typer.confirm("Confirm: Create PR?", abort=True)
        response = client.create_pull_request(
            title=title,
            description=description,
            targets=[
                {
                    "repositoryName": repo,
                    "sourceReference": source_branch,
                    "destinationReference": destination_branch,
                },
            ],
        )
        pr_id = response["pullRequest"]["pullRequestId"]
        pr_data = response["pullRequest"]

        region_name = session.region_name
        print(f"[bold green]Pull Request created successfully![/bold green] ID: {pr_id}\nPR DATA:")
        print(pr_data)
        print(f"GO TO PR! -> https://us-east-1.console.aws.amazon.com/codesuite/codecommit/repositories/{repo}/pull-requests/{pr_id}/details?region={region_name}")

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        print(f"[bold red]ERROR: {error_code}[/bold red] - {error_message}")

        if error_code == "RepositoryDoesNotExistException":
            print(f"[yellow]The repository <{repo}> does not exist. Check the name and try again.[/yellow]")
        elif error_code == "BranchDoesNotExistException":
            print("[yellow]One of the branches does not exist. Verify the branch names.[/yellow]")
        elif error_code == "InvalidReferenceNameException":
            print("[yellow]The branch name is invalid.[/yellow]")
        elif error_code == "PullRequestAlreadyExistsException":
            print("[yellow]A Pull Request with the same source and destination already exists.[/yellow]")
        else:
            print("[yellow]An unknown error occurred. Check the logs for more details.[/yellow]")

        raise typer.Exit(code=1)


@app.command()
def pr_list(
        max: Annotated[int, typer.Argument()],
    ) -> None:
    logger.debug("List PR Task initialized")
    
    try:
        client: CodeCommitClient = PERSONAL_AWS_CONFIG.get("client")
    except:
        typer.Exit(code=1)
    
    response = client.list_pull_requests(
        repositoryName=PERSONAL_AWS_CONFIG.get("DEFAULT_REPO"),
        maxResults=max
    )
    
    pr_list: List[str] = response["pullRequestIds"]
    
    
    for pr_id in pr_list:
        response = client.get_pull_request(
            pullRequestId=pr_id,
        )
        response = response["pullRequest"]
        pr_detail_obj = {
            "pullRequestId": response["pullRequestId"],
            "title": response["title"],
            "description": response.get("description", None),
            "pullRequestStatus": response.get("pullRequestStatus", None),
            "sourceReference": response["pullRequestTargets"][0]["sourceReference"],
            "destinationReference": response["pullRequestTargets"][0]["destinationReference"],
            "isMerged": response["pullRequestTargets"][0]["mergeMetadata"]["isMerged"],
            "GO_TO_PR": f"https://us-east-1.console.aws.amazon.com/codesuite/codecommit/repositories/{PERSONAL_AWS_CONFIG.get('DEFAULT_REPO')}/pull-requests/{pr_id}/details?region={PERSONAL_AWS_CONFIG.get('session').region_name}"
        }
        
        print(pr_detail_obj)
    print(pr_list)



@app.command()
def pr_close(
        pr_id: Annotated[str, typer.Argument()],
    ) -> None:
    logger.debug("Close PR Task initialized")
    
    try:
        client: CodeCommitClient = PERSONAL_AWS_CONFIG.get("client")
    except:
        typer.Exit(code=1)
    
    try:
        response = client.update_pull_request_status(
            pullRequestId=pr_id,
            pullRequestStatus="CLOSED"
        )
        print(f"[bold green]Pull Request {pr_id} closed successfully![/bold green]")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        
        print(f"[bold red]ERROR: {error_code}[/bold red] - {error_message}")
        
        if error_code == "PullRequestDoesNotExistException":
            print(f"[yellow]The Pull Request <{pr_id}> does not exist. Check the ID and try again.[/yellow]")
        else:
            print("[yellow]An unknown error occurred. Check the logs for more details.[/yellow]")
        
        raise typer.Exit(code=1)