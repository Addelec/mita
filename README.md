# Overview
A small CLI to store and insert frequently used commands/snippets, based on fzf.

Press the hotkey in your shell (default: Ctrl+G) to open a fuzzy list of your saved entries. Pick one and it will be appended to your command line, ready to edit before running.

It supports persistent variables and Jinja2 templates (these are separate from shell variables and are meant for seldom-changed values like paths or IPs). Regular shell variables can still be used inside commands.

# Install
Requirements: fzf and python3.

Then:

```bash
git clone https://github.com/addelec/mita.git
cd mita
chmod +x setup.sh
./setup.sh
```

# Usage
- Configure paths inside the `mita` file.
- Place `mita` somewhere on your PATH, then run `mita` to open the picker.
- This also enables the built-in commands

* Behavior
  - Running the program without finder mode (no -f) prints the selected entry followed by a newline — useful for pipes and scripts.
  - Finder mode (-f) suppresses the trailing newline so the selection can be inserted directly into an interactive prompt (terminal integration).

# Shell integration
Wire it up so the selected entry is inserted directly into your current prompt. Note: built-in commands (e.g., editing) are not yet supported here.

Example for zsh:

```bash
function phonebook_widget_zsh() {
  local cmd
  # Adjust the paths below
  cmd=$(/path/to/venv/bin/python3 /path/to/src/main.py -f)
  if [[ -n "$cmd" ]]; then
    LBUFFER+="$cmd"
  fi
  zle redisplay
}
zle -N phonebook-widget phonebook_widget_zsh
bindkey '^g' phonebook-widget
```

# Notes
By default, the sqlite database is stored at `~/.config/mita/database.db`.
