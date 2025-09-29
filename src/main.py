#!/usr/bin/env python3

import click
from jinja2 import Environment, BaseLoader

import db
from utils import fuzzy_select
from commands import handle_system_commands, SYSTEM_COMMANDS, add_command
from constants import NAME, VERSION

system_command_labels = [cmd["label"] for cmd in SYSTEM_COMMANDS]

@click.group(context_settings=dict(help_option_names=["-h", "--help"]), invoke_without_command=True)
@click.pass_context
@click.version_option(version=VERSION, prog_name=NAME)
@click.option("-f", "--find", "find_mode", is_flag=True, help="Starts in finder mode. Useful for shell integration.")
@click.option("-n", "--no-render", is_flag=True, help="Skips the jinja2 rendering step.")
def cli(ctx: click.Context, find_mode: bool, no_render: bool):
    """Command and Variable Manager using fuzzy finder."""
    if ctx.invoked_subcommand:
        return

    con = db.load_database()

    # Build label list
    commands = db.list_commands(con)
    labels = [cmd[1] for cmd in commands]
    if not find_mode:
        labels += system_command_labels

    selection_label = fuzzy_select(labels, "Select command")
    if not selection_label:
        return

    # System command path
    if selection_label in system_command_labels:
        command = next(cmd for cmd in SYSTEM_COMMANDS if cmd["label"] == selection_label)
        handle_system_commands(con, command)
        return

    # User command path
    command_row = next(cmd for cmd in commands if cmd[1] == selection_label)
    command_text = command_row[2]

    if no_render:
        text_to_display = command_text
    else:
        template = Environment(loader=BaseLoader()).from_string(command_text)
        variables = db.get_variables(con)
        variables_dict = {var[0]: var[1] for var in variables}
        text_to_display = template.render(variables_dict)

    # Output (finder mode avoids trailing newline)
    click.echo(text_to_display, nl=not find_mode)


@cli.group(name="commands")
def commands_group():
    """Manage user commands."""
    pass


@commands_group.command("add")
@click.option("-c", "--command", "command_to_add", required=True, help="Add a new command")
@click.option("-l", "--label", help="Set the label when adding a command (optional)")
def add_cmd(command_to_add: str, label: str | None):
    """Add a new command."""
    con = db.load_database()
    final_label = label or command_to_add
    add_command(con, command_to_add, final_label)


@cli.group(name="vars")
def vars_group():
    """Manage variables."""
    pass


@vars_group.command("set")
@click.argument("name_value")
def set_var(name_value: str):
    """Set a variable using NAME=VALUE."""
    con = db.load_database()
    if "=" not in name_value:
        raise click.BadParameter("Expected format NAME=VALUE.")
    name, value = name_value.split("=", 1)
    db.set_variable(con, name, value)


if __name__ == "__main__":
    cli()
