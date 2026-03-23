# creator.py

**Path:** src/projs/cli/creator.py
**Syntax:** python
**Generated:** 2026-03-22 18:36:59

```python
"""
projs.cli.creator - Interactive project creation and import flow.

Separation of concerns
-----------------------
  Gathering   _prompt_*() methods collect data from the user and update
              the draft after each step via DraftStore.save().

  Execution   execute() does all disk work — mkdir, README, docs/, gitignore,
              LICENSE — then promotes the draft to a permanent manifest.

  Entry points
    run()         — interactive new project (CLI)
    run_import()  — interactive import of existing directory (CLI)
    resume(draft) — re-enter gathering from a saved draft
    execute(draft)— shared backend; called by CLI and GUI alike
"""

from datetime import datetime
from typing import List, Optional

from projs.config import ConfigManager
from projs.manifest import (
    DraftStore,
    ManifestStore,
    ProjectDraft,
    ProjectManifest,
    ManifestCommand,
)
from projs.commands import CommandLibrary
from projs.language_actions import LanguageActions
from projs.cli.prompts import PromptHelper, UserCancelled
from projs.cli.menu_builder import MenuBuilder


class ProjectCreator:
    """Handles interactive project creation and import."""

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
        self.draft_store = DraftStore(config)

    # ------------------------------------------------------------------
    # Entry points
    # ------------------------------------------------------------------

    def run(self):
        """Interactive new project flow."""
        print("\n" + "=" * 50)
        print("Create New Project")
        print("=" * 50)

        draft = ProjectDraft.new(is_import=False)
        self.draft_store.save(draft)
        self._gather(draft)

    def run_import(self):
        """Interactive import of an existing project directory."""
        print("\n" + "=" * 50)
        print("Import Existing Project")
        print("=" * 50)

        draft = ProjectDraft.new(is_import=True)
        self.draft_store.save(draft)
        self._gather(draft)

    def resume(self, draft: ProjectDraft):
        """Resume gathering from a saved draft (new or import)."""
        kind = "import" if draft.is_import else "new project"
        print(f"\nResuming {kind} draft: {draft.display_name()}")
        self._gather(draft, start_step=draft.step)

    # ------------------------------------------------------------------
    # Gathering — updates and saves draft after each step
    # ------------------------------------------------------------------

    def _gather(self, draft: ProjectDraft, start_step: int = 0):
        """Run through all gathering steps, saving draft after each."""
        try:
            # Step 0 — name
            if start_step <= 0:
                draft.step = 0
                if draft.is_import:
                    draft.name = self._prompt_name_import()
                else:
                    draft.name = self._prompt_name_new()
                self.draft_store.save(draft)

            # Step 1 — description
            if start_step <= 1:
                draft.step = 1
                current = f" [{draft.description}]" if draft.description else ""
                draft.description = self.prompt.text(
                    f"Project description{current}"
                ).strip() or draft.description or ""
                self.draft_store.save(draft)

            # Step 2 — path
            if start_step <= 2:
                draft.step = 2
                draft.path = self._prompt_path(draft)
                self.draft_store.save(draft)

            # Step 3 — language
            if start_step <= 3:
                draft.step = 3
                draft.language = self._prompt_language()
                self.draft_store.save(draft)

            # Step 4 — license
            # Import: skip entirely if LICENSE file already exists.
            if start_step <= 4:
                draft.step = 4
                if draft.is_import:
                    project_path = draft.expanded_path()
                    if (project_path / "LICENSE").exists():
                        print("  ✓ LICENSE already exists — skipping.")
                        draft.license = "existing"
                    else:
                        draft.license = self._prompt_license()
                else:
                    draft.license = self._prompt_license()
                self.draft_store.save(draft)

            # Step 5 — gitignore
            # Import: skip if .gitignore exists; offer full prompt if missing.
            if start_step <= 5:
                draft.step = 5
                if draft.is_import:
                    draft.gitignore = self._prompt_gitignore_import(draft)
                else:
                    draft.gitignore = self._prompt_gitignore(draft.language)
                self.draft_store.save(draft)

            # Step 6 — commands
            if start_step <= 6:
                draft.step = 6
                draft.commands = self._prompt_commands(is_import=draft.is_import)
                self.draft_store.save(draft)

            # Step 7 — options (README, docs)
            # Import: only offer each item if it's absent from the directory.
            if start_step <= 7:
                draft.step = 7
                if draft.is_import:
                    draft.create_readme, draft.create_docs = (
                        self._prompt_scaffold_import(draft)
                    )
                else:
                    draft.create_readme = self.prompt.yes_no(
                        "Create README.md?", default=True
                    )
                    draft.create_docs = self.prompt.yes_no(
                        "Create docs/ directory?", default=False
                    )
                self.draft_store.save(draft)

            # Dry-run and confirm
            if self._show_dryrun(draft):
                self.execute(draft)
            else:
                print("\nProject creation cancelled.")
                if self.prompt.yes_no("Keep draft for later?", default=True):
                    print(f"  Draft saved: {draft.display_name()}")
                else:
                    self.draft_store.discard(draft)
                    print("  Draft discarded.")

        except UserCancelled:
            print("\nCancelled.")
            if self.prompt.yes_no("Keep draft for later?", default=True):
                print(f"  Draft saved: {draft.display_name()}")
            else:
                self.draft_store.discard(draft)
                print("  Draft discarded.")

    # ------------------------------------------------------------------
    # Shared execution backend — called by CLI and GUI
    # ------------------------------------------------------------------

    def execute(self, draft: ProjectDraft) -> Optional[ProjectManifest]:
        """
        Perform all disk operations and promote draft to manifest.

        Steps
        -----
          1. Create project directory (skipped for imports)
          2. Write .gitignore if entries exist
          3. Write LICENSE from template if license is set and not "existing"
          4. Create README.md if requested
          5. Create docs/ directory if requested
          6. Promote draft → manifest (saves manifest, deletes draft)

        Returns the new ProjectManifest, or None if execution failed.
        """
        project_path = draft.expanded_path()

        try:
            if not draft.is_import:
                project_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Created directory: {project_path}")
            else:
                if not project_path.exists():
                    print(f"✗ Directory not found: {project_path}")
                    return None

            if draft.gitignore:
                gitignore_path = project_path / ".gitignore"
                gitignore_path.write_text("\n".join(draft.gitignore) + "\n")
                print("✓ Created .gitignore")

            if draft.license and draft.license != "existing":
                self._write_license(project_path, draft.license)

            if draft.create_readme:
                readme_path = project_path / "README.md"
                if not readme_path.exists() or not draft.is_import:
                    readme_path.write_text(
                        f"# {draft.name}\n\n{draft.description or ''}\n"
                    )
                    print("✓ Created README.md")

            if draft.create_docs:
                docs_path = project_path / "docs"
                docs_path.mkdir(exist_ok=True)
                print("✓ Created docs/")

        except OSError as exc:
            print(f"✗ Error during project setup: {exc}")
            return None

        manifest = self.draft_store.promote(draft)
        print(f"\n✓ Project '{manifest.name}' created successfully!")
        print(f"  Directory: {project_path}")
        print(f"  Manifest:  ~/.projects/manifests/{manifest.name}.json")
        return manifest

    def _write_license(self, project_path, license_id: str) -> None:
        """Write a LICENSE file from the shipped template for the given license."""
        template = self.config.get_license_template(license_id)
        if template is None:
            print(f"  Note: no template found for '{license_id}' — LICENSE not written.")
            return

        author = self.config.get_author() or "Unknown"
        year = str(datetime.now().year)
        content = template.format(year=year, author=author)

        license_path = project_path / "LICENSE"
        license_path.write_text(content)
        print(f"✓ Created LICENSE ({license_id})")

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------

    def _prompt_name_new(self) -> str:
        """Prompt for a new project name, validate uniqueness."""
        while True:
            name = self.prompt.text("Project name").strip()
            if not name:
                print("Project name cannot be empty.")
                continue
            if self.manifest_store.load(name):
                print(f"Project '{name}' already exists.")
                continue
            return name

    def _prompt_name_import(self) -> str:
        """Prompt for a name when importing — uniqueness still required."""
        while True:
            name = self.prompt.text("Project name (for manifest)").strip()
            if not name:
                print("Project name cannot be empty.")
                continue
            if self.manifest_store.load(name):
                print(f"A manifest named '{name}' already exists.")
                continue
            return name

    def _prompt_path(self, draft: ProjectDraft) -> str:
        """Prompt for project path, defaulting sensibly."""
        if draft.is_import:
            default = draft.path or f"~/projects/{draft.name}"
            raw = self.prompt.text(
                f"Path to existing directory [{default}]"
            ).strip()
            return raw or default
        else:
            default = f"~/projects/{draft.name}"
            raw = self.prompt.text(
                f"Project directory [{default}]"
            ).strip()
            return raw or default

    def _prompt_language(self) -> str:
        """Prompt for programming language. Raises UserCancelled if user quits."""
        languages = self.config.get_languages()
        idx = self.prompt.choice("Select language", languages)
        if idx == len(languages) - 1:  # "other"
            return self.prompt.text("Enter language name").strip()
        return languages[idx]

    def _prompt_license(self) -> str:
        """Prompt for license type. Raises UserCancelled if user quits."""
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
            print(f"No standard entries for {language}.")

        if self.prompt.yes_no("Add custom entries?", default=False):
            print("Enter custom entries (one per line, blank line to finish):")
            while True:
                custom = self.prompt.text("Entry").strip()
                if not custom:
                    break
                entries.append(custom)

        return entries

    def _prompt_gitignore_import(self, draft: ProjectDraft) -> List[str]:
        """
        Import variant: skip if .gitignore exists; run full prompt if missing.
        """
        project_path = draft.expanded_path()
        if (project_path / ".gitignore").exists():
            print("  ✓ .gitignore already exists — skipping.")
            return []
        print("\n  No .gitignore found.")
        if self.prompt.yes_no("Create .gitignore?", default=True):
            return self._prompt_gitignore(draft.language)
        return []

    def _prompt_scaffold_import(self, draft: ProjectDraft):
        """
        Import variant for README and docs/.

        Scans the project directory and only prompts for items that are absent.
        Returns (create_readme, create_docs).
        """
        project_path = draft.expanded_path()

        if (project_path / "README.md").exists():
            print("  ✓ README.md already exists — skipping.")
            create_readme = False
        else:
            print("\n  No README.md found.")
            create_readme = self.prompt.yes_no("Create README.md?", default=True)

        if (project_path / "docs").exists():
            print("  ✓ docs/ already exists — skipping.")
            create_docs = False
        else:
            print("\n  No docs/ directory found.")
            create_docs = self.prompt.yes_no("Create docs/ directory?", default=False)

        return create_readme, create_docs

    def _prompt_commands(self, is_import: bool = False) -> List[ManifestCommand]:
        """Prompt for commands to associate with project."""
        commands = []

        print("\n-- Commands Setup --")
        print("Note: 'cd {project_dir}' is always run first automatically (seq 0).")
        print("Commands are executed in sequence order.\n")

        # Offer default editor as launch command
        editor = self.config.get_editor()
        if editor:
            if self.prompt.yes_no(
                f"Add '{editor} .' as launch command?", default=True
            ):
                commands.append(ManifestCommand(
                    seq=90,
                    command=f"{editor} .",
                    description=f"Launch {editor}",
                ))
                print(f"✓ Added: [90] {editor} .")
            else:
                choice = self.menu_builder.display_menu("editor_menu")
                if choice == "custom_editor":
                    selected_editor = self.prompt.text("Editor command").strip()
                elif choice == "back":
                    selected_editor = None
                else:
                    selected_editor = choice

                if selected_editor:
                    commands.append(ManifestCommand(
                        seq=90,
                        command=f"{selected_editor} .",
                        description=f"Launch {selected_editor}",
                    ))
                    print(f"✓ Added: [90] {selected_editor} .")

        # Command library loop
        while True:
            all_cmds = self.command_library.get_all()

            # Filter out create_only commands when importing
            if is_import:
                all_cmds = [
                    cmd for cmd in all_cmds
                    if "create_only" not in cmd.get("tags", [])
                ]

            if not all_cmds:
                print("No commands available in library.")
                break

            print("\nCommand library:")
            for i, cmd in enumerate(all_cmds, 1):
                display_cmd = cmd.get("command") or cmd.get("create_command", "")
                print(f"  {i}. {cmd['name']}  ({display_cmd})")
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

            if choice == len(all_cmds) + 1:
                cmd_str = self.prompt.text("Command").strip()
                if not cmd_str:
                    continue
                desc = self.prompt.text("Description (optional)").strip()
                seq = self._next_seq(commands)
                commands.append(ManifestCommand(
                    seq=seq, command=cmd_str, description=desc
                ))
                print(f"✓ Added: [{seq}] {cmd_str}")
            else:
                selected = all_cmds[choice - 1]
                name = selected["name"]
                desc = self.prompt.text(
                    f"Description [{name}]"
                ).strip() or name
                seq = self._next_seq(commands)
                commands.append(ManifestCommand(
                    seq=seq,
                    command=selected["id"],
                    description=desc,
                ))
                print(f"✓ Added: [{seq}] {name}")

        return commands


    # ------------------------------------------------------------------
    # Dry-run display
    # ------------------------------------------------------------------

    def _show_dryrun(self, draft: ProjectDraft) -> bool:
        """Show a consistent dry-run summary of the draft and confirm."""

        def _val(v) -> str:
            return str(v) if v not in (None, "", []) else "—"

        print("\n" + "=" * 50)
        print("DRY-RUN: Project Configuration")
        print("=" * 50)

        print(f"\n  Name:        {_val(draft.name)}")
        print(f"  Description: {_val(draft.description)}")
        print(f"  Language:    {_val(draft.language)}")
        print(f"  License:     {_val(draft.license)}")
        print(f"  Path:        {_val(draft.path)}")
        print(f"  Is import:   {'yes' if draft.is_import else 'no'}")
        print(f"  README:      {'yes' if draft.create_readme else 'no'}")
        print(f"  Docs dir:    {'yes' if draft.create_docs else 'no'}")

        print("\n  .gitignore entries:")
        if draft.gitignore:
            for entry in draft.gitignore:
                print(f"    • {entry}")
        else:
            print("    —")

        print("\n  Launch sequence:")
        expanded = draft.expanded_path() if draft.path else "—"
        print(f"    [  0] cd {expanded}  (automatic)")

        if draft.language:
            lang_actions = LanguageActions(self.config, draft.language)
            all_actions = lang_actions.get_all()
            if all_actions:
                print(f"\n  Language actions ({draft.language}):")
                for action in all_actions:
                    aname = action.get("name", "unnamed")
                    kind = action.get("type", "unknown")
                    print(f"    • {aname} ({kind})")

        if draft.commands:
            for cmd in sorted(draft.commands, key=lambda c: c.seq):
                desc = f"  # {cmd.description}" if cmd.description else ""
                print(f"    [{cmd.seq:>3}] {cmd.command}{desc}")
        else:
            print("    —")

        print("\n" + "=" * 50)
        return self.prompt.yes_no("Proceed?", default=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _next_seq(self, current_commands: List[ManifestCommand]) -> int:
        """Auto-assign next seq number, skipping 90 (reserved for editor)."""
        used = {c.seq for c in current_commands}
        seq = 10
        while seq in used or seq == 90:
            seq += 10
        return seq

```
