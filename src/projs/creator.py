"""
projs.creator - Interactive project creation flow
"""

from pathlib import Path
from typing import List
import json

from projs.config import ConfigManager
from projs.manifest import ManifestStore, ProjectManifest, ManifestCommand
from projs.prompts import PromptHelper
from projs.commands import CommandLibrary
from projs.menu_builder import MenuBuilder
from projs.language_actions import LanguageActions


class ProjectCreator:
    """Handles interactive project creation."""

    def __init__(
        self,
        config: ConfigManager,
        manifest_store: ManifestStore,
        prompt: PromptHelper,
    ):
        self.config = config
        self.manifest_store = manifest_store
        self.prompt = prompt
        self.command_library = CommandLibrary(config)
        self.menu_builder = MenuBuilder(config, prompt)

    def run(self):
        """Run the interactive project creation flow."""
        print("\n-- Project Details --")

        name = self._prompt_name()
        description = self.prompt.text("Project description")
        language = self._prompt_language()
        license_type = self._prompt_license()
        gitignore = self._prompt_gitignore(language)
        commands = self._prompt_commands()

        manifest = ProjectManifest(
            name=name,
            description=description,
            language=language,
            path=f"~/projects/{name}",
            license=license_type,
            gitignore=gitignore,
            commands=commands,
        )

        if self._show_dryrun(manifest):
            project_path = manifest.expanded_path()
            project_path.mkdir(parents=True, exist_ok=True)

            if self.prompt.yes_no("Create README.md?", default=True):
                readme_path = project_path / "README.md"
                readme_path.write_text(f"# {name}\n\n{description}\n")
                print(f"✓ Created README.md")

            self.manifest_store.save(manifest)
            print(f"\n✓ Project '{name}' created successfully!")
            print(f"  Directory: {project_path}")
            print(f"  Manifest: ~/.projects/manifests/{name}.json")
        else:
            print("\nProject creation cancelled.")

    def _prompt_name(self) -> str:
        """Prompt for project name, validate uniqueness."""
        while True:
            name = self.prompt.text("Project name").strip()

            if not name:
                print("Project name cannot be empty.")
                continue

            if self.manifest_store.load(name):
                print(f"Project '{name}' already exists.")
                continue

            return name

    def _prompt_language(self) -> str:
        """Prompt for programming language."""
        languages = self.config.get_languages()
        idx = self.prompt.choice("Select language", languages)

        if idx == len(languages) - 1:  # "other"
            return self.prompt.text("Enter language name").strip()

        return languages[idx]

    def _prompt_license(self) -> str:
        """Prompt for license type."""
        licenses = self.config.get_licenses()
        idx = self.prompt.choice("Select license", licenses)

        if idx == len(licenses) - 1:  # "Custom/Other"
            return self.prompt.text("Enter license name").strip()

        return licenses[idx]

    def _prompt_gitignore(self, language: str) -> List[str]:
        """Prompt for gitignore entries."""
        entries = self.config.get_gitignore(language).copy()

        print("\n-- .gitignore Setup --")
        if entries:
            print(f"Standard entries for {language}:")
            for entry in entries:
                print(f"  • {entry}")
        else:
            print(f"No standard entries for {language}")

        if self.prompt.yes_no("Add custom entries?", default=False):
            print("Enter custom entries (one per line, blank line to finish):")
            while True:
                custom = self.prompt.text("Entry").strip()
                if not custom:
                    break
                entries.append(custom)

        return entries

    def _prompt_commands(self) -> List[ManifestCommand]:
        """Prompt for commands to associate with project."""
        commands = []

        print("\n-- Commands Setup --")
        print("Note: 'cd {project_dir}' is always run first automatically (seq 0).")
        print("Commands are executed in sequence order.\n")

        # If editor is set, offer to add it as the last command
        editor = self.config.get_editor()
        if editor:
            if self.prompt.yes_no(f"Add '{editor} .' as launch command?", default=True):
                # Suggest seq 90 so it runs last by convention
                commands.append(ManifestCommand(
                    seq=90,
                    command=f"{editor} .",
                    description=f"Launch {editor}",
                ))
                print(f"✓ Added: [{90}] {editor} .")

        while True:
            all_cmds = self.command_library.get_all()
            if not all_cmds:
                print("No commands available in library.")
                break

            print("\nCommand library:")
            for i, cmd in enumerate(all_cmds, 1):
                print(f"  {i}. {cmd['name']}  ({cmd['command']})")
            print(f"  {len(all_cmds) + 1}. Add custom command")
            print(f"  {len(all_cmds) + 2}. Done")

            while True:
                try:
                    choice = int(input("Selection: ").strip())
                    if 1 <= choice <= len(all_cmds) + 2:
                        break
                    print(f"Please select 1-{len(all_cmds) + 2}.")
                except ValueError:
                    print("Please enter a number.")

            if choice == len(all_cmds) + 2:
                break
            elif choice == len(all_cmds) + 1:
                # Custom command
                cmd_str = self.prompt.text("Command").strip()
                if not cmd_str:
                    continue
                desc = self.prompt.text("Description (optional)").strip()
                seq = self._prompt_seq(commands)
                commands.append(ManifestCommand(seq=seq, command=cmd_str, description=desc))
                print(f"✓ Added: [{seq}] {cmd_str}")
            else:
                # Library command
                selected = all_cmds[choice - 1]
                desc = self.prompt.text(
                    f"Description",
                    default=selected['name']
                ).strip()
                seq = self._prompt_seq(commands)
                commands.append(ManifestCommand(
                    seq=seq,
                    command=selected['id'],
                    description=desc,
                ))
                print(f"✓ Added: [{seq}] {selected['name']}")

        return commands

    def _prompt_seq(self, current_commands: List[ManifestCommand]) -> int:
        """Prompt for sequence number, suggesting next available."""
        if current_commands:
            suggested = max(c.seq for c in current_commands) + 10
            # Don't suggest past the editor slot (90)
            if suggested >= 90:
                suggested = 90 - 10
        else:
            suggested = 10

        while True:
            try:
                raw = self.prompt.text(f"Sequence number", default=str(suggested)).strip()
                seq = int(raw)
                if seq == 0:
                    print("Seq 0 is reserved for 'cd {project_dir}'.")
                    continue
                if seq == 90 and any(c.seq == 90 for c in current_commands):
                    print("Seq 90 is already used. Choose another.")
                    continue
                return seq
            except ValueError:
                print("Please enter a number.")

    def _show_dryrun(self, manifest: ProjectManifest) -> bool:
        """Show dry-run of what will be created and ask for confirmation."""
        print("\n" + "=" * 50)
        print("DRY-RUN: Project Configuration")
        print("=" * 50)

        data = manifest.to_dict()
        print("\nManifest:")
        print(json.dumps(data, indent=2))

        print("\n" + "-" * 50)
        print("Files to be created:")
        print("-" * 50)
        print(f"  ~/.projects/manifests/{manifest.name}.json")

        print("\n" + "-" * 50)
        print("Actions on launch (in sequence order):")
        print("-" * 50)
        print(f"  [  0] cd {manifest.expanded_path()}  (automatic)")

        lang_actions = LanguageActions(self.config, manifest.language)
        all_actions = lang_actions.get_all()
        if all_actions:
            print(f"\n  Language-specific actions ({manifest.language}):")
            for action in all_actions:
                print(f"         • {action.get('name', 'unnamed')} ({action.get('type', 'unknown')})")

        print()
        for cmd in manifest.sorted_commands():
            desc = f"  # {cmd.description}" if cmd.description else ""
            print(f"  [{cmd.seq:>3}] {cmd.command}{desc}")

        print("\n" + "=" * 50)
        return self.prompt.yes_no("Proceed with creation?", default=True)
