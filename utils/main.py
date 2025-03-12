from logging import Logger
from typing import Any, Callable, Dict, Optional

import typer


def prompt_input(
        caller: Callable,
        logger: Logger,
        params: Dict[str, Any],
        msg: Optional[str] = "Source branch (press h to list [- for name filter]): ",
    )-> str:
        source_branch = None
        
        def _msg(_msg: Optional[str] = ""):
            return typer.prompt(text=_msg)

        while True:
            source_branch = _msg(msg)
            
            help_requested = source_branch.startswith("h")
            
            if source_branch is not None and not help_requested:
                return source_branch
    
            if help_requested:
                logger.debug("User request for help")
                name_filter = None
                try:
                    name_filter = source_branch.split("-")[1]
                except IndexError as k:
                    logger.info(f"Error reading user input: {k}")
                response = caller(**params)

                output = []

                if name_filter is not None:
                    logger.debug("Name filtered requested")
                    for branch_name in response["branches"]:
                        if name_filter in branch_name:
                            output.append(branch_name)  
                else:
                    output = response["branches"]    
                print(output)