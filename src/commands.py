from utils import create_system_command, select_command, select_variable
from constants import NAME

import db
import click


def add_command(con, cmd, label):
    if label.lower().startswith(f"{NAME.lower()}"):
        print(f"Command starts with {NAME}, not adding.")
        return
    
    db.add_command_label(con, label, cmd)
    
def handle_add_command(con):
    edited_cmd = click.edit(text="\n", extension=".sh")
    if edited_cmd is None:
        command = click.prompt("Enter command to add", default="", show_default=False)
    else:
        command = edited_cmd.rstrip("\n")

    label = click.prompt("Enter label", default=command, show_default=True)
    
    if not label:
        label = command
    
    if label.lower().startswith(f"{NAME.lower()}"):
        print(f"Command starts with {NAME}, not adding.")
        return
    
    db.add_command_label(con, label, command)

def handle_swap_variable_state(con):
  var = select_variable(con)
  
  if var:
    db.swap_variable(con, var[0])
    

def handle_set_variable(con):
    var = select_variable(con, prompt="Select variable (esc to create)")
    
    if var:
        name = var[0]
        value = click.prompt(f"Enter new value for {name}", default=var[1], show_default=True)
        db.set_variable(con, name, value)
        
    else:
        pair = click.prompt("Enter variable to set (name=value)")
        if "=" not in pair:
            click.echo("Invalid format. Use name=value.")
            return
        name, value = pair.split("=", 1)
        db.set_variable(con, name, value)
  

def handle_delete_variable(con):
    var = select_variable(con)
    
    if var:
        db.delete_variable(con, var[0])

def handle_delete_command(con):
    command = select_command(con)
    
    if command:
        db.delete_command_id(con, command[0])
        print(f"Deleted command: {command[1]}")
    

def handle_modify_command(con):

    command = select_command(con)
    if not command:
        return

    cmd_id, current_label, current_cmd = command[0], command[1], command[2]

    # Prefill command for editing in $EDITOR; fallback to prompt with default
    edited_cmd = click.edit(text=f"{current_cmd}\n", extension=".sh")
    if edited_cmd is None:
        new_command = click.prompt("Enter new command", default=current_cmd, show_default=True)
    else:
        new_command = edited_cmd.rstrip("\n")

    new_label = click.prompt("Enter new label", default=current_label, show_default=True)

    db.modify_command(con, cmd_id, new_command, new_label)
    click.echo(f"Modified command: {current_label} to {new_command}")

SYSTEM_COMMANDS = [
    create_system_command("swap", handle_swap_variable_state),
    create_system_command("delete variable", handle_delete_variable),
    create_system_command("delete command", handle_delete_command),
    create_system_command("modify command", handle_modify_command),
    create_system_command("add command", handle_add_command),
    create_system_command("set variable", handle_set_variable),
]


def handle_system_commands(con, command):
    command["function"](con)
  