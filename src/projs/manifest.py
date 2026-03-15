"""
projs.manifest - Project manifest models and storage

Command sequence rules:
  - seq 0 is reserved: cd {project_path} — automatic, never stored in manifest
  - seq numbers are non-consecutive by convention (10, 20, 30...) to allow insertion
  - launcher.py sorts by seq at runtime before executing
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from projs.config import ConfigManager


class ManifestCommand:
    """Represents a single sequenced command in a project manifest."""

    def __init__(self, seq: int, command: str, description: str = ""):
        self.seq = seq
        self.command = command
        self.description = description

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ManifestCommand":
        return cls(
            seq=data["seq"],
            command=data["command"],
            description=data.get("description", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seq": self.seq,
            "command": self.command,
            "description": self.description,
        }

    def __repr__(self):
        return f"[{self.seq:>3}] {self.command}"


class ProjectManifest:
    """Represents a single project's configuration."""

    def __init__(
        self,
        name: str,
        description: str,
        language: str,
        path: str,
        license: str,
        gitignore: List[str],
        commands: List[ManifestCommand],
    ):
        self.name = name
        self.description = description
        self.language = language
        self.path = path
        self.license = license
        self.gitignore = gitignore
        self.commands = commands

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectManifest":
        """Create manifest from dictionary (loaded from JSON)."""
        raw_commands = data.get("commands", [])

        # Handle legacy manifests where commands were plain strings
        commands = []
        for i, cmd in enumerate(raw_commands):
            if isinstance(cmd, str):
                commands.append(ManifestCommand(seq=(i + 1) * 10, command=cmd))
            else:
                commands.append(ManifestCommand.from_dict(cmd))

        return cls(
            name=data["name"],
            description=data["description"],
            language=data["language"],
            path=data["path"],
            license=data["license"],
            gitignore=data.get("gitignore", []),
            commands=commands,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "language": self.language,
            "path": self.path,
            "license": self.license,
            "gitignore": self.gitignore,
            "commands": [cmd.to_dict() for cmd in self.sorted_commands()],
        }

    def sorted_commands(self) -> List[ManifestCommand]:
        """Return commands sorted by seq number."""
        return sorted(self.commands, key=lambda c: c.seq)

    def next_seq(self) -> int:
        """Suggest next available seq number (last + 10, or 10 if empty)."""
        if not self.commands:
            return 10
        return max(c.seq for c in self.commands) + 10

    def expanded_path(self) -> Path:
        """Return path with ~ expanded to home directory."""
        return Path(self.path).expanduser()


class ManifestStore:
    """Handles loading and saving project manifests."""

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager

    def load(self, project_name: str) -> Optional[ProjectManifest]:
        """Load a project manifest by name."""
        path = self.config.manifest_path(project_name)
        if not path.exists():
            return None

        data = json.loads(path.read_text())
        return ProjectManifest.from_dict(data)

    def save(self, manifest: ProjectManifest) -> None:
        """Save a project manifest (creates new or overwrites existing)."""
        path = self.config.manifest_path(manifest.name)
        path.write_text(json.dumps(manifest.to_dict(), indent=2))

    def backup_and_save(self, manifest: ProjectManifest) -> None:
        """Backup existing manifest (if any) and save new one."""
        existing = self.load(manifest.name)
        if existing:
            backup_path = self.config.backup_path(manifest.name)
            backup_path.write_text(json.dumps(existing.to_dict(), indent=2))

        self.save(manifest)

    def list_all(self) -> List[ProjectManifest]:
        """List all project manifests."""
        manifests = []
        for path in sorted(self.config.manifests_dir.glob("*.json")):
            data = json.loads(path.read_text())
            manifests.append(ProjectManifest.from_dict(data))
        return manifests
