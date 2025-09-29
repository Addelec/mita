import sqlite3
import os
from constants import DB_SCHEMA_VERSION as VERSION

# Database location
DATABASE_LOCATION = os.path.join(os.path.expanduser("~"), ".config", "mita", "database.db")

os.makedirs(os.path.dirname(DATABASE_LOCATION), exist_ok=True)

def load_database():
  con = sqlite3.connect(DATABASE_LOCATION)
  
  # Check if the database has the correct version
  if not check_version(con):
    return None
  
  # Check if the tables exist
  check_create_tables(con)
  
  return con
  

# Function to check if the database has the correct version (using user_version)
# If no version is found it will set it to the current programed version
def check_version(con):
  cur = con.cursor()
  
  cur.execute("PRAGMA user_version")
  db_version = cur.fetchone()[0]
  
  if db_version == VERSION:
    return True
  
  # For newly created databases set the version to the current version
  if db_version == 0:
      print(f"Setting database version to {VERSION}")
      cur.execute(f"PRAGMA user_version = {VERSION}")
      return True
    
  
  if db_version != VERSION:
    print(f"Database version mismatch: {db_version} != {VERSION}")
    return False
  
  return True

# Make sure the relevant tables exists
def check_create_tables(con):
  try:
    cur = con.cursor()
    
    # Check if the command table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commands'")
    
    if cur.fetchone() is None:
      print("Creating commands table")
      cur.execute('''
        CREATE TABLE commands (
          id INTEGER PRIMARY KEY,
          label TEXT NOT NULL,
          command TEXT NOT NULL
        )
      ''')
    
    # Check if the variables table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='variables'")
    
    if cur.fetchone() is None:
      print("Creating variables table")
      cur.execute('''
        CREATE TABLE variables (
          name TEXT PRIMARY KEY,
          value TEXT NOT NULL,
          past_value TEXT
        )
      ''')
    
    con.commit()
  except sqlite3.Error as e:
    print(f"Error creating tables: {e}")
    return False
  
  return True
  
def add_command_label(con, label, command):
  try:
    cur = con.cursor() 
    
    # Check if the command already exists
    cur.execute("SELECT * FROM commands WHERE command = ? and label = ?", (command,label))
    if cur.fetchone() is not None:
      print(f"Command already exists: {command}")
      return False
    
    cur.execute("INSERT INTO commands (label, command) VALUES (?, ?)", (label, command))
    print(f"Added command: {label} -> {command}")
    
    con.commit()
    return True
  except sqlite3.Error as e:
    print(f"Error adding command: {e}")
    return False
  
def add_command(con, command):
  return add_command_label(con, command, command)

def modify_command(con, id, command, label):
  try:
    cur = con.cursor()
    
    cur.execute("UPDATE commands SET command = ?, label = ? WHERE id = ?", (command, label, id))
    
    con.commit()
    return True
  except sqlite3.Error as e:
    print(f"Error modifying command: {e}")
    return False
  
def delete_command_cmd(con, command):
  try:
    cur = con.cursor()
    
    cur.execute("DELETE FROM commands WHERE command = ?", (command,))
    
    con.commit()
    return True
  except sqlite3.Error as e:
    print(f"Error deleting command: {e}")
    return False
  
def delete_command_id(con, id):
  try:
    cur = con.cursor()
    
    cur.execute("DELETE FROM commands WHERE id = ?", (id,))
    
    con.commit()
    return True
  except sqlite3.Error as e:
    print(f"Error deleting command: {e}")
    return False
  
def list_commands(con):
  try:
    cur = con.cursor()
    
    cur.execute("SELECT * FROM commands")
    commands = cur.fetchall()
    return commands
  except sqlite3.Error as e:
    print(f"Error listing commands: {e}")
    return []
  
def get_variables(con):
  try:
    cur = con.cursor()
    
    cur.execute("SELECT * FROM variables")
    variables = cur.fetchall()
    return variables
  except sqlite3.Error as e:
    print(f"Error listing variables: {e}")
    return []

def set_variable(con, name, value):
  try:
    cur = con.cursor()
    
    # Retrieve the current value of the variable, if it exists
    cur.execute("SELECT value FROM variables WHERE name = ?", (name,))
    row = cur.fetchone()
    past_value = row[0] if row else None

    # Update or insert the variable with the new value and past_value
    if past_value is not None:
      cur.execute("UPDATE variables SET value = ?, past_value = ? WHERE name = ?", (value, past_value, name))
    else:
      cur.execute("INSERT INTO variables (name, value, past_value) VALUES (?, ?, ?)", (name, value, past_value))
    
    con.commit()
    
    
    return True
  except sqlite3.Error as e:
    print(f"Error setting variable: {e}")
    return False
  

def swap_variable(con, name):
  try:
    cur = con.cursor()
    
    # Retrieve the current value of the variable
    cur.execute("SELECT value, past_value FROM variables WHERE name = ?", (name,))
    row = cur.fetchone()
    
    if row is None:
      print(f"Variable {name} does not exist.")
      return False
    
    
    # Check if the variable has a past value
    if row[1] is None:
      print(f"Variable {name} does not have a past value.")
      return False
    
    current_value, past_value = row
    
    print(f"Swapping variable {name}: current value = {current_value}, past value = {past_value}")
    
    # Swap the values
    cur.execute("UPDATE variables SET value = ?, past_value = ? WHERE name = ?", (past_value, current_value, name))
    
    con.commit()
    return True
  except sqlite3.Error as e:
    print(f"Error swapping variable: {e}")
    return False

def delete_variable(con, name):
  try:
    cur = con.cursor()
    
    cur.execute("DELETE FROM variables WHERE name = ?", (name,))
    
    con.commit()
    return True
  except sqlite3.Error as e:
    print(f"Error deleting variable: {e}")
    return False