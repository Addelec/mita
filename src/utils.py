import subprocess
import os

from constants import NAME
import db

def create_system_command(name, function):
    return {
      "name": name,
      "function": function,
      "label": (NAME) + ": " + name
    }
    
def fuzzy_select(commands, prompt):
    p = subprocess.Popen(
        ['fzf', '--prompt', prompt + "> "],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    input_str = "\n".join(commands)
    out, _ = p.communicate(input=input_str)
    return out.strip()

def select_variable(con, prompt="Select variable"):
    variables = db.get_variables(con)
    
    if not variables:
        print("No variables in phonebook. Use -s to set (var=val).")
        return
    
    labels = [var[0] for var in variables]
    selection = fuzzy_select(labels, prompt)
    
    if selection:
        variable = [var for var in variables if var[0] == selection][0]
        return variable
    else:
        return None  

def select_command(con, prompt="Select command"):
    commands = db.list_commands(con)
    
    if not commands:
        print("No commands in phonebook. Use -a to add.")
        return
    
    labels = [cmd[1] for cmd in commands]
    selection = fuzzy_select(labels, prompt)
    
    if selection:
        command = [cmd for cmd in commands if cmd[1] == selection][0]
        return command
    else:
        return None
    