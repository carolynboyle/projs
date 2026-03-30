# projs_menus_yaml_with_ide.txt

**Path:** docs/yaml/projs_menus_yaml_with_ide.txt
**Syntax:** text
**Generated:** 2026-03-25 09:30:03

```text
# projs menu definitions
# All menus are defined here and loaded dynamically
# New menus can be added without changing code

main_menu:
  name: "main_menu"
  title: "PROJS - Project Manager"
  items:
    - id: list_projects
      display: "List projects"
    - id: create_project
      display: "Create new project"
    - id: launch_project
      display: "Launch project"
    - id: modify_project
      display: "Modify project"
    - id: settings
      display: "Settings"
    - id: help
      display: "Help"
    - id: quit
      display: "Quit"

settings_menu:
  name: "settings_menu"
  title: "SETTINGS"
  items:
    - id: edit_editor
      display: "Edit Editor"
    - id: edit_ide
      display: "Edit IDE"
    - id: edit_package_manager
      display: "Edit Package Manager"
    - id: view_config
      display: "View Configuration File"
    - id: back
      display: "Back to Main Menu"

help_menu:
  name: "help_menu"
  title: "HELP - projs Documentation"
  items:
    - id: view_help
      display: "View Help (README)"
    - id: back
      display: "Back to Main Menu"

ide_menu:
  name: "ide_menu"
  title: "Select Code Editor/IDE"
  items:
    - id: nano
      display: "nano"
    - id: vim
      display: "vim"
    - id: codium
      display: "Codium"
    - id: vscode
      display: "Visual Studio Code"
    - id: emacs
      display: "Emacs"
    - id: custom_ide
      display: "Enter custom editor"
    - id: back
      display: "Back to commands"

```
