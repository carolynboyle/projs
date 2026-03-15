#!/usr/bin/env python3
"""
projs - Project launcher and setup manager
Main CLI entry point with menu-driven interface.
"""

import sys
import os
import argparse
from pathlib import Path
import pydoc

from projs.config import ConfigManager
from projs.manifest import ManifestStore
from projs.prompts import PromptHelper
from projs.menu_builder import MenuBuilder
from projs.creator import ProjectCreator
from projs.launcher import ProjectLauncher
from projs.modifier import ProjectModifier


class ProjectsApp:
    """Main application class for the projs CLI."""

    def __init__(self):
        self.config = ConfigManager()
        self._check_first_run()
        self.manifest_store = ManifestStore(self.config)
        self.prompt = PromptHelper()
        self.menu_builder = MenuBuilder(self.config, self.prompt)

    def _check_first_run(self):
        """Initialize projs on first run if config doesn't exist."""
        from projs._setup import initialize_projs

        if not self.config.system_file.exists():
            print("First run: Initializing projs...")
            initialize_projs()
            self.config = ConfigManager()

    def main_menu(self):
        """Main menu loop."""
        while True:
            os.system("clear")
            choice = self.menu_builder.display_menu("main_menu")

            if choice == "list_projects":
                self.list_projects()
            elif choice == "create_project":
                self.create_project()
            elif choice == "launch_project":
                self.launch_project()
            elif choice == "modify_project":
                self.modify_project()
            elif choice == "settings":
                self.settings_menu()
            elif choice == "help":
                self.help_menu()
            elif choice in ("quit", "back"):
                print("Goodbye!")
                break
            else:
                print(f"Error: unknown menu choice '{choice}', check menus.yaml")
                input("Press Enter to continue...")

    def list_projects(self):
        """List all projects with descriptions."""
        manifests = self.manifest_store.list_all()

        if not manifests:
            print("\nNo projects found.")
            input("Press Enter to continue...")
            return

        print("\n" + "=" * 50)
        print("Projects:")
        print("=" * 50)
        for i, manifest in enumerate(manifests, 1):
            print(f"\n{i}. {manifest.name}")
            print(f"   Language:    {manifest.language}")
            print(f"   License:     {manifest.license}")
            print(f"   Path:        {manifest.path}")
            print(f"   Description: {manifest.description}")
            print(f"   Commands:")
            print(f"     [  0] cd {manifest.expanded_path()}  (automatic)")
            for cmd in manifest.sorted_commands():
                desc = f"  # {cmd.description}" if cmd.description else ""
                print(f"     [{cmd.seq:>3}] {cmd.command}{desc}")

        input("\nPress Enter to continue...")

    def create_project(self):
        """Create a new project (interactive flow)."""
        print("\n" + "=" * 50)
        print("Create New Project")
        print("=" * 50)

        creator = ProjectCreator(self.config, self.manifest_store, self.prompt)
        creator.run()

        input("\nPress Enter to continue...")

    def launch_project(self):
        """Launch a project by selection."""
        manifests = self.manifest_store.list_all()

        if not manifests:
            print("\nNo projects found.")
            input("Press Enter to continue...")
            return

        print("\nSelect a project to launch:")
        options = [f"{m.name} ({m.language})" for m in manifests]
        choice_idx = self.prompt.choice("Project", options)

        selected = manifests[choice_idx]
        launcher = ProjectLauncher(self.config, selected, self.prompt)
        launcher.run()

    def modify_project(self):
        """Modify an existing project."""
        manifests = self.manifest_store.list_all()

        if not manifests:
            print("\nNo projects found.")
            input("Press Enter to continue...")
            return

        print("\nSelect a project to modify:")
        options = [f"{m.name} ({m.language})" for m in manifests]
        choice_idx = self.prompt.choice("Project", options)

        selected = manifests[choice_idx]
        modifier = ProjectModifier(self.config, self.manifest_store, selected, self.prompt)
        modifier.run()

        input("\nPress Enter to continue...")

    def settings_menu(self):
        """Settings submenu."""
        while True:
            os.system("clear")
            choice = self.menu_builder.display_menu("settings_menu")

            if choice == "edit_editor":
                self._edit_editor()
            elif choice == "edit_package_manager":
                self._edit_package_manager()
            elif choice == "view_config":
                self._view_config_file()
            elif choice == "reset_defaults":
                self._reset_defaults()
            elif choice == "back":
                break

    def _edit_editor(self):
        """Edit the preferred editor using the editor menu."""
        print("\n-- Edit Preferred Editor --")
        print(f"Current: {self.config.get_editor() or 'not set'}")

        choice = self.menu_builder.display_menu("editor_menu")

        if choice == "back":
            return
        elif choice == "custom_editor":
            editor = self.prompt.text("Editor command").strip()
            if not editor:
                return
        else:
            editor = choice

        self.config.system["editor"] = editor
        self.config.save_system(self.config.system)
        print(f"✓ Editor updated to: {editor}")
        input("\nPress Enter to continue...")

    def _edit_package_manager(self):
        """Edit the package manager preference."""
        print("\n-- Edit Package Manager --")
        print(f"Current: {self.config.get_package_manager()}")

        # Load options from platforms.yaml
        options = self._get_package_manager_options()
        if options:
            print("\nKnown options:")
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")
            print(f"  {len(options) + 1}. Enter custom")

            while True:
                try:
                    choice = int(input("Selection: ").strip())
                    if 1 <= choice <= len(options):
                        pkg_mgr = options[choice - 1]
                        break
                    elif choice == len(options) + 1:
                        pkg_mgr = self.prompt.text("Package manager").strip()
                        if pkg_mgr:
                            break
                        print("Cannot be empty.")
                    else:
                        print(f"Please select 1-{len(options) + 1}.")
                except ValueError:
                    print("Please enter a number.")
        else:
            pkg_mgr = self.prompt.text("Package manager").strip()
            if not pkg_mgr:
                return

        self.config.system["package_manager"] = pkg_mgr
        self.config.save_system(self.config.system)
        print(f"✓ Package manager updated to: {pkg_mgr}")
        input("\nPress Enter to continue...")

    def _get_package_manager_options(self) -> list:
        """Load all known package manager options from platforms.yaml."""
        import yaml
        from projs._setup import _DATA_DIR
        platforms_file = _DATA_DIR / "platforms.yaml"

        if not platforms_file.exists():
            return []

        try:
            data = yaml.safe_load(platforms_file.read_text())
            options = []
            for platform_data in data.values():
                if isinstance(platform_data, dict):
                    for opt in platform_data.get("options", []):
                        if opt not in options:
                            options.append(opt)
            return options
        except Exception:
            return []

    def _view_config_file(self):
        """Display the system configuration file."""
        print("\n-- System Configuration --")
        print(f"Location: {self.config.system_file}")
        print()

        try:
            config_text = self.config.system_file.read_text()
            pydoc.pager(config_text)
        except Exception as e:
            print(f"Error reading config: {e}")

        input("\nPress Enter to continue...")

    def _reset_defaults(self):
        """Reset config files to shipped defaults."""
        print("\n-- Reset to Defaults --")
        print("This will overwrite your config files with shipped defaults.")
        print("Your manifests and project files will not be affected.")

        if not self.prompt.yes_no("Are you sure?", default=False):
            print("Reset cancelled.")
            input("\nPress Enter to continue...")
            return

        from projs._setup import _DATA_DIR
        import shutil

        copies = [
            (_DATA_DIR / "defaults.yaml", self.config.defaults_file),
            (_DATA_DIR / "menus.yaml",    self.config.menus_file),
        ]

        for src, dst in copies:
            if not src.exists():
                print(f"Warning: shipped default not found: {src}")
                continue
            try:
                shutil.copy2(src, dst)
                print(f"✓ Reset {dst.name}")
            except Exception as e:
                print(f"✗ Error resetting {dst.name}: {e}")

        # Reload config
        self.config = ConfigManager()
        self.menu_builder = MenuBuilder(self.config, self.prompt)
        print("\n✓ Defaults restored. Configuration reloaded.")
        input("\nPress Enter to continue...")

    def help_menu(self):
        """Help menu."""
        while True:
            os.system("clear")
            choice = self.menu_builder.display_menu("help_menu")

            if choice == "view_help":
                self._view_help()
            elif choice == "back":
                break

    def _view_help(self):
        """Display help and documentation."""
        readme_path = Path(__file__).parent.parent.parent / "README.md"

        if readme_path.exists():
            try:
                readme_text = readme_path.read_text()
                if readme_text.strip():
                    pydoc.pager(readme_text)
                else:
                    print("\n[README.md is empty]")
            except Exception as e:
                print(f"\nError reading README: {e}")
        else:
            print("\n[Help files will be here]")
            print(f"\nREADME location: {readme_path}")
            print("\nIn the meantime, use the menus to:")
            print("  1. Create new projects")
            print("  2. List your projects")
            print("  3. Launch projects in tmux")
            print("  4. Modify project settings")
            print("  5. Configure your preferences")

        input("\nPress Enter to continue...")


def cli():
    """Entry point for the projs command."""
    parser = argparse.ArgumentParser(
        description="projs - Project launcher and setup manager"
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Command: 'new', 'launch <name>', 'list', or leave blank for interactive menu"
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments for the command"
    )

    parsed = parser.parse_args()
    app = ProjectsApp()

    if not parsed.command:
        app.main_menu()
        return

    if parsed.command == "list":
        app.list_projects()
    elif parsed.command == "new":
        app.create_project()
    elif parsed.command == "launch" and parsed.args:
        project_name = parsed.args[0]
        manifest = app.manifest_store.load(project_name)
        if not manifest:
            print(f"Project '{project_name}' not found.")
            sys.exit(1)
        launcher = ProjectLauncher(app.config, manifest, app.prompt)
        launcher.run()
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
