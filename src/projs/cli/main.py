#!/usr/bin/env python3
"""
projs - Project launcher and setup manager
Main CLI entry point with menu-driven interface.
"""

import sys
import os
import argparse
import shutil
from pathlib import Path
import pydoc

import yaml

from projs.config import ConfigManager
from projs.manifest import ManifestStore, DraftStore
from projs._setup import initialize_projs, _DATA_DIR
from projs.cli.prompts import PromptHelper, UserCancelled
from projs.cli.menu_builder import MenuBuilder
from projs.cli.creator import ProjectCreator
from projs.cli.launcher import ProjectLauncher
from projs.cli.modifier import ProjectModifier


class ProjectsApp:
    """Main application class for the projs CLI."""

    def __init__(self):
        self.config = ConfigManager()
        self._check_first_run()
        self.manifest_store = ManifestStore(self.config)
        self.draft_store = DraftStore(self.config)
        self.prompt = PromptHelper()
        self.menu_builder = MenuBuilder(self.config, self.prompt)

    def _check_first_run(self):
        """Initialize projs on first run if config doesn't exist."""
        if not self.config.system_file.exists():
            print("First run: Initializing projs...")
            initialize_projs()
            self.config = ConfigManager()

    def _check_pending_drafts(self):
        """On startup, offer to resume or discard any saved drafts."""
        drafts = self.draft_store.list_all()
        if not drafts:
            return

        print(f"\n{'=' * 50}")
        print(f"  {len(drafts)} unfinished draft(s) found:")
        print(f"{'=' * 50}")
        for i, draft in enumerate(drafts, 1):
            print(f"  {i}. {draft.display_name()}")

        print("\nOptions:")
        print("  r — resume a draft")
        print("  d — discard a draft")
        print("  s — skip (handle later)")

        while True:
            choice = input("\nChoice [r/d/s]: ").strip().lower()
            if choice == "s":
                return
            elif choice == "r":
                if len(drafts) == 1:
                    idx = 0
                else:
                    try:
                        idx = self.prompt.choice(
                            "Resume which draft",
                            [d.display_name() for d in drafts],
                        )
                    except UserCancelled:
                        return
                creator = ProjectCreator(
                    self.config, self.manifest_store, self.prompt
                )
                creator.resume(drafts[idx])
                input("\nPress Enter to continue...")
                return
            elif choice == "d":
                if len(drafts) == 1:
                    idx = 0
                else:
                    try:
                        idx = self.prompt.choice(
                            "Discard which draft",
                            [d.display_name() for d in drafts],
                        )
                    except UserCancelled:
                        return
                self.draft_store.discard(drafts[idx])
                print(f"  Draft discarded: {drafts[idx].display_name()}")
                input("\nPress Enter to continue...")
                return
            else:
                print("Please enter r, d, or s.")

    def main_menu(self):
        """Main menu loop."""
        self._check_pending_drafts()

        while True:
            os.system("clear")
            choice = self.menu_builder.display_menu("main_menu")

            if choice == "list_projects":
                self.list_projects()
            elif choice == "create_project":
                self.create_project()
            elif choice == "import_project":
                self.import_project()
            elif choice == "launch_project":
                self.launch_project()
            elif choice == "modify_project":
                self.modify_project()
            elif choice == "delete_project":
                self.delete_project()
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

        lines = []
        lines.append("=" * 50)
        lines.append("Projects:")
        lines.append("=" * 50)
        for i, manifest in enumerate(manifests, 1):
            lines.append(f"\n{i}. {manifest.name}")
            lines.append(f"   Language:    {manifest.language}")
            lines.append(f"   License:     {manifest.license}")
            lines.append(f"   Path:        {manifest.path}")
            lines.append(f"   Description: {manifest.description}")
            lines.append("   Commands:")
            lines.append(f"     [  0] cd {manifest.expanded_path()}  (automatic)")
            for cmd in manifest.sorted_commands():
                desc = f"  # {cmd.description}" if cmd.description else ""
                lines.append(f"     [{cmd.seq:>3}] {cmd.command}{desc}")

        pydoc.pager("\n".join(lines))

    def create_project(self):
        """Create a new project (interactive flow)."""
        creator = ProjectCreator(self.config, self.manifest_store, self.prompt)
        creator.run()
        input("\nPress Enter to continue...")

    def import_project(self):
        """Import an existing project directory."""
        creator = ProjectCreator(self.config, self.manifest_store, self.prompt)
        creator.run_import()
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
        try:
            choice_idx = self.prompt.choice("Project", options)
        except UserCancelled:
            return

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
        try:
            choice_idx = self.prompt.choice("Project", options)
        except UserCancelled:
            return

        selected = manifests[choice_idx]
        modifier = ProjectModifier(self.config, self.manifest_store, selected, self.prompt)
        modifier.run()

        input("\nPress Enter to continue...")

    def delete_project(self):
        """Delete an existing project (with double confirmation)."""
        manifests = self.manifest_store.list_all()

        if not manifests:
            print("\nNo projects found.")
            input("Press Enter to continue...")
            return

        print("\nSelect a project to delete:")
        options = [f"{m.name} ({m.language})" for m in manifests]
        try:
            choice_idx = self.prompt.choice("Project", options)
        except UserCancelled:
            return
        selected = manifests[choice_idx]

        print(f"\nYou are about to delete '{selected.name}'.")
        print("This cannot be undone.")
        if not self.prompt.yes_no("Are you sure?", default=False):
            print("Delete cancelled.")
            input("\nPress Enter to continue...")
            return

        print(f"\nFinal confirmation: permanently delete '{selected.name}'?")
        if not self.prompt.yes_no("Confirm delete", default=False):
            print("Delete cancelled.")
            input("\nPress Enter to continue...")
            return

        self.manifest_store.delete(selected.name)
        print(f"\n✓ Project '{selected.name}' deleted.")
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
        except Exception:  # pylint: disable=broad-except
            return []

    def _view_config_file(self):
        """Display the system configuration file."""
        print("\n-- System Configuration --")
        print(f"Location: {self.config.system_file}")
        print()

        try:
            config_text = self.config.system_file.read_text()
            pydoc.pager(config_text)
        except Exception as e:  # pylint: disable=broad-except
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
            except Exception as e:  # pylint: disable=broad-except
                print(f"✗ Error resetting {dst.name}: {e}")

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
            except Exception as e:  # pylint: disable=broad-except
                print(f"\nError reading README: {e}")
        else:
            print(f"\nREADME not found at {readme_path}")
            print("The package may be incomplete. Consider reinstalling.")

        input("\nPress Enter to continue...")


def cli():
    """Entry point for the projs command."""
    parser = argparse.ArgumentParser(
        description="projs - Project launcher and setup manager"
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Command: 'new', 'import', 'launch <n>', 'list', or leave blank for interactive menu"
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
    elif parsed.command == "import":
        app.import_project()
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
