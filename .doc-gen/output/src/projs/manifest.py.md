# manifest.py

**Path:** src/projs/manifest.py
**Syntax:** python
**Generated:** 2026-03-19 14:56:23

```python
"""
projs.manifest - Project manifest models and storage

Command sequence rules:
  - seq 0 is reserved: cd {project_path} — automatic, never stored in manifest
  - seq numbers are non-consecutive by convention (10, 20, 30...) to allow insertion
  - launcher.py sorts by seq at runtime before executing

Draft lifecycle:
  - ProjectDraft holds partial data while creation/import is in progress
  - Saved to ~/.projects/drafts/draft_<timestamp>.json after each step
  - Promoted to a full ProjectManifest on completion, draft file deleted
  - On startup, existing drafts are listed and user may resume or discard
"""

import json
from datetime import datetime
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
        """Create a ManifestCommand from a dictionary."""
        return cls(
            seq=data["seq"],
            command=data["command"],
            description=data.get("description", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ManifestCommand to dictionary."""
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
        proj_license: str,
        gitignore: List[str],
        commands: List[ManifestCommand],
        create_docs: bool = False,
    ):
        self.name = name
        self.description = description
        self.language = language
        self.path = path
        self.license = proj_license
        self.gitignore = gitignore
        self.commands = commands
        self.create_docs = create_docs

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
            proj_license=data["license"],
            gitignore=data.get("gitignore", []),
            commands=commands,
            create_docs=data.get("create_docs", False),
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
            "create_docs": self.create_docs,
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


class ProjectDraft:
    """
    Partial project configuration assembled during creation or import.

    All project fields are optional — only what has been collected so far
    is populated. The draft is saved to disk after each step so that an
    interrupted session can be resumed.

    Fields:
        created_at  ISO timestamp string, matches the draft filename.
        step        How far the wizard/prompts had progressed (0-based).
        is_import   True when importing an existing directory; causes
                    execute() to skip the mkdir step.
    """

    def __init__(
        self,
        created_at: str,
        step: int = 0,
        is_import: bool = False,
        name: Optional[str] = None,
        description: Optional[str] = None,
        language: Optional[str] = None,
        path: Optional[str] = None,
        proj_license: Optional[str] = None,
        gitignore: Optional[List[str]] = None,
        commands: Optional[List[ManifestCommand]] = None,
        create_readme: bool = True,
        create_docs: bool = False,
    ):
        self.created_at = created_at
        self.step = step
        self.is_import = is_import
        self.name = name
        self.description = description
        self.language = language
        self.path = path
        self.license = proj_license
        self.gitignore = gitignore or []
        self.commands = commands or []
        self.create_readme = create_readme
        self.create_docs = create_docs

    @classmethod
    def new(cls, is_import: bool = False) -> "ProjectDraft":
        """Create a fresh draft with a timestamp."""
        return cls(
            created_at=datetime.now().strftime("%Y%m%d_%H%M%S"),
            is_import=is_import,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectDraft":
        """Load a draft from a dictionary (read from disk)."""
        raw_commands = data.get("commands", [])
        commands = [ManifestCommand.from_dict(c) for c in raw_commands]

        return cls(
            created_at=data["created_at"],
            step=data.get("step", 0),
            is_import=data.get("is_import", False),
            name=data.get("name"),
            description=data.get("description"),
            language=data.get("language"),
            path=data.get("path"),
            proj_license=data.get("license"),
            gitignore=data.get("gitignore", []),
            commands=commands,
            create_readme=data.get("create_readme", True),
            create_docs=data.get("create_docs", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize draft to dictionary for JSON storage."""
        return {
            "created_at": self.created_at,
            "step": self.step,
            "is_import": self.is_import,
            "name": self.name,
            "description": self.description,
            "language": self.language,
            "path": self.path,
            "license": self.license,
            "gitignore": self.gitignore,
            "commands": [c.to_dict() for c in self.commands],
            "create_readme": self.create_readme,
            "create_docs": self.create_docs,
        }

    def is_complete(self) -> bool:
        """Return True if all required fields are populated."""
        return all([self.name, self.language, self.path, self.license])

    def to_manifest(self) -> "ProjectManifest":
        """
        Promote this draft to a ProjectManifest.

        Only call after is_complete() returns True.
        """
        return ProjectManifest(
            name=self.name,
            description=self.description or "",
            language=self.language,
            path=self.path,
            proj_license=self.license,
            gitignore=self.gitignore,
            commands=self.commands,
            create_docs=self.create_docs,
        )

    def display_name(self) -> str:
        """Human-readable label for listing drafts."""
        kind = "import" if self.is_import else "new"
        name = self.name or "unnamed"
        ts = self.created_at.replace("_", " ")
        return f"{name} ({kind}) — started {ts}"

    def __repr__(self):
        return f"ProjectDraft({self.created_at}, step={self.step}, name={self.name!r})"


class DraftStore:
    """Handles saving, loading, listing, and discarding project drafts."""

    _FILENAME_PREFIX = "draft_"

    def __init__(self, config: ConfigManager):
        self.config = config
        self._drafts_dir = config.drafts_dir
        self._drafts_dir.mkdir(parents=True, exist_ok=True)

    def save(self, draft: ProjectDraft) -> None:
        """Write draft to disk, overwriting any previous save for this draft."""
        path = self._path_for(draft)
        path.write_text(json.dumps(draft.to_dict(), indent=2))

    def discard(self, draft: ProjectDraft) -> None:
        """Delete a draft file from disk."""
        path = self._path_for(draft)
        if path.exists():
            path.unlink()

    def list_all(self) -> List[ProjectDraft]:
        """Return all drafts sorted oldest-first."""
        drafts = []
        pattern = f"{self._FILENAME_PREFIX}*.json"
        for path in sorted(self._drafts_dir.glob(pattern)):
            try:
                data = json.loads(path.read_text())
                drafts.append(ProjectDraft.from_dict(data))
            except Exception as exc:
                print(f"Warning: could not load draft {path.name}: {exc}")
        return drafts

    def promote(self, draft: ProjectDraft) -> ProjectManifest:
        """
        Convert a completed draft to a permanent manifest.

        Saves the manifest and deletes the draft file.
        Raises ValueError if the draft is not complete.
        """
        if not draft.is_complete():
            raise ValueError(
                f"Draft '{draft.name}' is missing required fields "
                "and cannot be promoted to a manifest."
            )
        manifest = draft.to_manifest()
        manifest_store = ManifestStore(self.config)
        manifest_store.save(manifest)
        self.discard(draft)
        return manifest

    def _path_for(self, draft: ProjectDraft) -> Path:
        return self._drafts_dir / f"{self._FILENAME_PREFIX}{draft.created_at}.json"


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

    def delete(self, project_name: str) -> None:
        """Delete a project manifest and its backup (if any)."""
        path = self.config.manifest_path(project_name)
        if path.exists():
            path.unlink()

        backup = self.config.backup_path(project_name)
        if backup.exists():
            backup.unlink()

```
