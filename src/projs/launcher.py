"""
projs.launcher - Project launch flow
"""

import subprocess
from pathlib import Path
from typing import List

from projs.config import ConfigManager
from projs.manifest import ProjectManifest, ManifestCommand
from projs.prompts import PromptHelper
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

    def run(self):
        """Launch the project: create tmux session, execute commands, attach."""
        project_path = self.manifest.expanded_path()

        # Verify project directory exists
        if not project_path.exists():
            print(f"\nError: Project directory does not exist: {project_path}")
            print(f"Create it first with: mkdir -p {project_path}")
            input("Press Enter to continue...")
            return

        print(f"\nLaunching project: {self.manifest.name}")
        print(f"Path: {project_path}")

        # Check if tmux is available
        if not self._tmux_available():
            print("\nError: tmux is not installed.")
            pkg = self.config.get_package_manager()
            if pkg and pkg != "unknown":
                print(f"Install it with: {pkg} install tmux")
            else:
                print("Install tmux using your system package manager.")
            input("Press Enter to continue...")
            return

        # Show launch plan if confirmations are on
        if self.config.get_preference("show_confirmations", True):
            self._show_launch_plan(project_path)
            if not self.prompt.yes_no("Proceed?", default=True):
                print("Launch cancelled.")
                return

        # Create tmux session (or reattach if exists)
        session = TMuxSession(self.manifest.name)
        is_new_session = not session.session_exists()

        try:
            session.create()
            if is_new_session:
                print(f"✓ TMux session '{self.manifest.name}' created")
            else:
                print(f"✓ Reattaching to existing session '{self.manifest.name}'")
        except Exception as e:
            print(f"Error creating tmux session: {e}")
            input("Press Enter to continue...")
            return

        # Only run startup commands on new sessions
        if is_new_session:
            self._execute_commands(session, project_path)
        else:
            print("  (skipping startup commands — session already running)")

        # Attach user to the session
        print("\nAttaching to session...")
        try:
            session.attach()
        except Exception as e:
            print(f"Error attaching to session: {e}")
            input("Press Enter to continue...")

    def _tmux_available(self) -> bool:
        """Check if tmux is installed."""
        try:
            subprocess.run(
                ["tmux", "-V"],
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _show_launch_plan(self, project_path: Path):
        """Show what will be executed before launching."""
        print("\n" + "-" * 50)
        print("Launch plan:")
        print("-" * 50)
        print(f"  [  0] cd {project_path}  (automatic)")
        for cmd in self.manifest.sorted_commands():
            resolved = self._resolve_command(cmd.command)
            desc = f"  # {cmd.description}" if cmd.description else ""
            print(f"  [{cmd.seq:>3}] {resolved}{desc}")
        print("-" * 50)

    def _execute_commands(self, session: TMuxSession, project_path: Path):
        """Execute all commands in the manifest in sequence order."""
        print(f"\nExecuting startup commands...")

        # seq 0: always cd to project directory first
        session.send_command(f"cd {project_path}")

        # Execute manifest commands in seq order
        for cmd in self.manifest.sorted_commands():
            resolved = self._resolve_command(cmd.command)
            if resolved:
                print(f"  → [{cmd.seq:>3}] {resolved}")
                session.send_command(resolved)

    def _resolve_command(self, cmd_spec: str) -> str:
        """Resolve a command spec to actual command string.

        cmd_spec can be:
        - A command ID from commands.json (e.g., "venv")
        - A custom command (e.g., "custom: ./setup.sh")  [legacy]
        - A literal command string (e.g., "codium .")
        """
        # Legacy: strip "custom: " prefix if present
        if cmd_spec.startswith("custom: "):
            return cmd_spec[8:]

        # Try to look up as command ID in library
        cmd_obj = self.command_library.get_by_id(cmd_spec)
        if cmd_obj:
            return cmd_obj["command"]

        # Treat as literal command string
        return cmd_spec
