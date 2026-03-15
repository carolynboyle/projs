"""
projs.modifier - Project modification flow
"""

import json
from typing import List

from projs.config import ConfigManager
from projs.manifest import ManifestStore, ProjectManifest, ManifestCommand
from projs.prompts import PromptHelper
from projs.commands import CommandLibrary


class ProjectModifier:
    """Handles project modification with backups."""

    def __init__(
        self,
        config: ConfigManager,
        manifest_store: ManifestStore,
        manifest: ProjectManifest,
        prompt: PromptHelper,
    ):
        self.config = config
        self.manifest_store = manifest_store
        self.manifest = manifest
        self.prompt = prompt
        self.command_library = CommandLibrary(config)

    def run(self):
        """Run the interactive project modification flow."""
        print(f"\n-- Modifying Project: {self.manifest.name} --")
        print(f"Description: {self.manifest.description}")
        print(f"Language:    {self.manifest.language}")
        print(f"License:     {self.manifest.license}")

        while True:
            print("\n" + "-" * 50)
            print("What would you like to modify?")
            print("-" * 50)
            print("1. Description")
            print("2. License")
            print("3. .gitignore")
            print("4. Commands")
            print("5. Done (save changes)")
            print("6. Cancel (discard changes)")
            print("-" * 50)

            choice = self.prompt.text("Select an option").strip()

            if choice == "1":
                self.manifest.description = self.prompt.text(
                    "New description",
                    default=self.manifest.description
                ).strip()

            elif choice == "2":
                self.manifest.license = self._prompt_license()

            elif choice == "3":
                self.manifest.gitignore = self._prompt_gitignore(
                    self.manifest.language,
                    current=self.manifest.gitignore
                )

            elif choice == "4":
                self.manifest.commands = self._prompt_commands(
                    current=self.manifest.commands
                )

            elif choice == "5":
                self._save_with_backup()
                print(f"\n✓ Project '{self.manifest.name}' updated successfully!")
                break

            elif choice == "6":
                print("\nChanges discarded.")
                break

            else:
                print("Invalid choice. Please select 1-6.")

    def _prompt_license(self) -> str:
        """Prompt for license type."""
        licenses = self.config.get_licenses()
        idx = self.prompt.choice("Select license", licenses)

        if idx == len(licenses) - 1:  # "Custom/Other"
            return self.prompt.text("Enter license name").strip()

        return licenses[idx]

    def _prompt_gitignore(
        self,
        language: str,
        current: List[str] = None
    ) -> List[str]:
        """Prompt for gitignore entries."""
        if current is None:
            current = []

        entries = current.copy()

        print("\n-- .gitignore Setup --")
        print("Current entries:")
        for entry in entries:
            print(f"  • {entry}")

        if self.prompt.yes_no("Reset to standard entries?", default=False):
            entries = self.config.get_gitignore(language).copy()
            print(f"Reset to standard entries for {language}")

        if self.prompt.yes_no("Add more entries?", default=False):
            print("Enter new entries (one per line, blank line to finish):")
            while True:
                custom = self.prompt.text("Entry").strip()
                if not custom:
                    break
                if custom not in entries:
                    entries.append(custom)
                else:
                    print(f"  ('{custom}' already in list)")

        if self.prompt.yes_no("Remove any entries?", default=False):
            while True:
                print("\nCurrent entries:")
                for i, entry in enumerate(entries, 1):
                    print(f"{i}. {entry}")

                remove_input = self.prompt.text(
                    "Enter number to remove (or blank to finish)"
                ).strip()

                if not remove_input:
                    break

                try:
                    idx = int(remove_input) - 1
                    if 0 <= idx < len(entries):
                        removed = entries.pop(idx)
                        print(f"Removed: {removed}")
                    else:
                        print(f"Please select 1-{len(entries)}.")
                except ValueError:
                    print("Please enter a number.")

        return entries

    def _prompt_commands(
        self,
        current: List[ManifestCommand] = None
    ) -> List[ManifestCommand]:
        """Prompt to modify commands."""
        if current is None:
            current = []

        commands = current.copy()

        while True:
            print("\n-- Commands --")
            print(f"  [  0] cd {self.manifest.expanded_path()}  (automatic)")
            if commands:
                for cmd in sorted(commands, key=lambda c: c.seq):
                    desc = f"  # {cmd.description}" if cmd.description else ""
                    print(f"  [{cmd.seq:>3}] {cmd.command}{desc}")
            else:
                print("  (no commands)")

            print("\n" + "-" * 50)
            print("1. Add command from library")
            print("2. Add custom command")
            print("3. Edit sequence number")
            print("4. Remove command")
            print("5. Done")
            print("-" * 50)

            choice = self.prompt.text("Select an option").strip()

            if choice == "1":
                commands = self._add_from_library(commands)

            elif choice == "2":
                commands = self._add_custom(commands)

            elif choice == "3":
                commands = self._edit_seq(commands)

            elif choice == "4":
                commands = self._remove_command(commands)

            elif choice == "5":
                break

            else:
                print("Invalid choice. Please select 1-5.")

        return commands

    def _add_from_library(
        self, commands: List[ManifestCommand]
    ) -> List[ManifestCommand]:
        """Add a command from the library."""
        all_cmds = self.command_library.get_all()
        if not all_cmds:
            print("No commands available in library.")
            return commands

        print("\nCommand library:")
        for i, cmd in enumerate(all_cmds, 1):
            print(f"  {i}. {cmd['name']}  ({cmd['command']})")

        while True:
            try:
                choice = int(self.prompt.text("Selection").strip())
                if 1 <= choice <= len(all_cmds):
                    break
                print(f"Please select 1-{len(all_cmds)}.")
            except ValueError:
                print("Please enter a number.")

        selected = all_cmds[choice - 1]
        desc = self.prompt.text("Description", default=selected['name']).strip()
        seq = self._prompt_seq(commands)
        commands.append(ManifestCommand(seq=seq, command=selected['id'], description=desc))
        print(f"✓ Added: [{seq}] {selected['name']}")
        return commands

    def _add_custom(
        self, commands: List[ManifestCommand]
    ) -> List[ManifestCommand]:
        """Add a custom command."""
        cmd_str = self.prompt.text("Command").strip()
        if not cmd_str:
            return commands
        desc = self.prompt.text("Description (optional)").strip()
        seq = self._prompt_seq(commands)
        commands.append(ManifestCommand(seq=seq, command=cmd_str, description=desc))
        print(f"✓ Added: [{seq}] {cmd_str}")
        return commands

    def _edit_seq(
        self, commands: List[ManifestCommand]
    ) -> List[ManifestCommand]:
        """Edit the sequence number of an existing command."""
        if not commands:
            print("No commands to edit.")
            return commands

        print("\nSelect command to resequence:")
        sorted_cmds = sorted(commands, key=lambda c: c.seq)
        for i, cmd in enumerate(sorted_cmds, 1):
            desc = f"  # {cmd.description}" if cmd.description else ""
            print(f"  {i}. [{cmd.seq:>3}] {cmd.command}{desc}")

        while True:
            try:
                choice = int(self.prompt.text("Selection").strip())
                if 1 <= choice <= len(sorted_cmds):
                    break
                print(f"Please select 1-{len(sorted_cmds)}.")
            except ValueError:
                print("Please enter a number.")

        cmd = sorted_cmds[choice - 1]
        print(f"Current seq: {cmd.seq}")

        while True:
            try:
                new_seq = int(self.prompt.text("New sequence number").strip())
                if new_seq == 0:
                    print("Seq 0 is reserved for 'cd {project_dir}'.")
                    continue
                cmd.seq = new_seq
                print(f"✓ Updated to [{new_seq}] {cmd.command}")
                break
            except ValueError:
                print("Please enter a number.")

        return commands

    def _remove_command(
        self, commands: List[ManifestCommand]
    ) -> List[ManifestCommand]:
        """Remove a command from the list."""
        if not commands:
            print("No commands to remove.")
            return commands

        print("\nSelect command to remove:")
        sorted_cmds = sorted(commands, key=lambda c: c.seq)
        for i, cmd in enumerate(sorted_cmds, 1):
            desc = f"  # {cmd.description}" if cmd.description else ""
            print(f"  {i}. [{cmd.seq:>3}] {cmd.command}{desc}")

        while True:
            try:
                choice = int(self.prompt.text("Selection").strip())
                if 1 <= choice <= len(sorted_cmds):
                    break
                print(f"Please select 1-{len(sorted_cmds)}.")
            except ValueError:
                print("Please enter a number.")

        removed = sorted_cmds[choice - 1]
        commands = [c for c in commands if c is not removed]
        print(f"✓ Removed: [{removed.seq}] {removed.command}")
        return commands

    def _prompt_seq(self, current_commands: List[ManifestCommand]) -> int:
        """Prompt for sequence number, suggesting next available."""
        if current_commands:
            suggested = max(c.seq for c in current_commands) + 10
            if suggested >= 90:
                suggested = 80
        else:
            suggested = 10

        while True:
            try:
                raw = self.prompt.text("Sequence number", default=str(suggested)).strip()
                seq = int(raw)
                if seq == 0:
                    print("Seq 0 is reserved for 'cd {project_dir}'.")
                    continue
                return seq
            except ValueError:
                print("Please enter a number.")

    def _save_with_backup(self):
        """Backup the old manifest and save the new one."""
        self.manifest_store.backup_and_save(self.manifest)
