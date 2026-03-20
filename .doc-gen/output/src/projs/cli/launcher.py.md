# launcher.py

**Path:** src/projs/cli/launcher.py
**Syntax:** python
**Generated:** 2026-03-19 14:56:23

```python
"""
projs.launcher - Project launch flow
"""

import subprocess
from pathlib import Path
from typing import List

from projs.config import ConfigManager
from projs.manifest import ProjectManifest
from projs.cli.prompts import PromptHelper
from projs.commands import CommandLibrary
from projs.tmux import TMuxSession


class ProjectLauncher:
    """Handles project launching and command execution."""
    
    def __init__(
        self,
        config: ConfigManager,
        manifest: ProjectManifest,
        prompt: PromptHelper,
    ):
        self.config = config
        self.manifest = manifest
        self.prompt = prompt
        self.command_library = CommandLibrary(config)
    
    def run(self, gui_mode: bool = False):
        """Launch the project: create tmux session, execute commands, attach.

        Args:
            gui_mode: When True, skips the blocking ``session.attach()`` call.
                      The tmux session is created and all commands are sent, but
                      the GUI remains responsive.  The user connects manually via
                      ``tmux attach-session -t <name>`` in their terminal.
                      When False (CLI default), attaches immediately and blocks
                      until the user exits tmux.
        """
        project_path = self.manifest.expanded_path()

        # Verify project directory exists
        if not project_path.exists():
            print(f"\nError: Project directory does not exist: {project_path}")
            print(f"Create it first with: mkdir -p {project_path}")
            if not gui_mode:
                input("Press Enter to continue...")
            return

        print(f"\nLaunching project: {self.manifest.name}")
        print(f"Path: {project_path}")

        # Create tmux session (or reattach if exists)
        session = TMuxSession(self.manifest.name)
        try:
            session.create()
            print(f"✓ TMux session '{self.manifest.name}' ready")
        except Exception as e:
            print(f"Error creating tmux session: {e}")
            if not gui_mode:
                input("Press Enter to continue...")
            return

        # Execute commands in the session
        self._execute_commands(session, project_path)

        if gui_mode:
            # Session is running detached — tell the user how to connect.
            print(f"\n✓ Session ready — attach with:")
            print(f"  tmux attach-session -t {self.manifest.name}")
        else:
            # CLI mode — block here until the user exits tmux.
            print("\nAttaching to session...")
            try:
                session.attach()
            except Exception as e:
                print(f"Error attaching to session: {e}")
                input("Press Enter to continue...")
    
    def _execute_commands(self, session: TMuxSession, project_path: Path):
        """Execute all commands in the manifest.

        Before firing each command the launcher evaluates two optional guard
        fields that can appear on any command library entry:

          idempotent_check  — relative path that must NOT exist for the command
                              to run.  If it already exists the command is skipped
                              silently (e.g. don't re-create .venv on every launch).

          requires_path     — relative path that MUST exist for the command to run.
                              If it is absent the command is skipped with a warning
                              (e.g. can't activate a venv that was never created).

        Custom commands (``custom: …``) and unresolved literals have no library
        entry and are always executed as-is.
        """
        print(f"\nExecuting commands in {self.manifest.name}...")

        # Always start with cd to project directory
        session.send_command(f"cd {project_path}")

        for cmd_spec in self.manifest.commands:
            cmd, cmd_obj = self._resolve_command(cmd_spec)
            if not cmd:
                continue

            # --- idempotent_check -------------------------------------------
            # Skip if the target path already exists (command already done).
            if cmd_obj:
                check = cmd_obj.get("idempotent_check")
                if check and (project_path / check).exists():
                    print(f"  ↷ skipped (already exists): {cmd_obj.get('name', cmd)}")
                    continue

            # --- requires_path -----------------------------------------------
            # Warn and skip if a prerequisite path is missing.
            if cmd_obj:
                req = cmd_obj.get("requires_path")
                if req and not (project_path / req).exists():
                    print(
                        f"  ✗ skipped — '{req}' not found "
                        f"(required by: {cmd_obj.get('name', cmd)})"
                    )
                    continue

            print(f"  → {cmd}")
            session.send_command(cmd)

    def _resolve_command(self, cmd_spec) -> tuple[str, dict | None]:
        """Resolve a command spec to (command_string, library_entry | None).

        cmd_spec may be a plain string or a ManifestCommand object (which
        carries .command and .seq attributes).  Both are normalised to a
        string before processing.

        Returns the raw command string and, if the spec matched a library
        entry, that entry dict (so the caller can inspect guard fields).
        Custom commands and unrecognised literals return None as the second
        element.

        cmd_spec can be:
        - A ManifestCommand object  (seq + command string inside)
        - A library ID              (e.g. "venv")
        - A custom command          (e.g. "custom: ./setup.sh")
        - A literal command         (e.g. "codium .")
        """
        # Unwrap ManifestCommand → plain string
        if hasattr(cmd_spec, "command"):
            cmd_spec = cmd_spec.command

        if cmd_spec.startswith("custom: "):
            return cmd_spec[8:], None  # strip prefix; no library entry

        cmd_obj = self.command_library.get_by_id(cmd_spec)
        if cmd_obj:
            return self._resolve_cmd_obj(cmd_obj), cmd_obj

        # Unrecognised — treat as a literal shell command, no guard fields.
        return cmd_spec, None

    def _resolve_cmd_obj(self, cmd_obj: dict) -> str:
        """Resolve a library entry to the correct command string.

        Handles the combined venv entry:
          .venv absent  → create_command  (create + activate in one shell op)
          .venv present → activate_command (activate only, never clobbers packages)

        All other entries use the plain "command" field.
        """
        venv_path = cmd_obj.get("venv_path")
        if venv_path:
            project_path = self.manifest.expanded_path()
            if (project_path / venv_path).exists():
                print(f"  ↷ venv exists — activating only")
                return cmd_obj["activate_command"]
            print(f"  + venv not found — creating and activating")
            return cmd_obj["create_command"]

        return cmd_obj.get("command", "")

```
