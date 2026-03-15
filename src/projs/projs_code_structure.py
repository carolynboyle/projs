# ============================================================================
# projs - Project launcher & setup manager
# ============================================================================
# Module Structure (to be split into separate files)
# ============================================================================

# config.py
# ============================================================================

from pathlib import Path
from datetime import datetime
import json
from typing import Optional, List, Dict, Any


class ConfigManager:
    """Manages ~/.projects/ directory structure and paths."""
    
    def __init__(self, config_root: Optional[Path] = None):
        """Initialize config manager with root directory."""
        self.root = config_root or (Path.home() / ".projects")
        self.manifests_dir = self.root / "manifests"
        self.backups_dir = self.root / "backups"
        self.templates_dir = self.root / "templates"
        self.language_actions_dir = self.root / "language-actions"
        self.commands_file = self.root / "commands.json"
        self.servers_file = self.root / "servers.yaml"
        
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Create all necessary directories if they don't exist."""
        for dir_path in [
            self.root,
            self.manifests_dir,
            self.backups_dir,
            self.templates_dir,
            self.language_actions_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def manifest_path(self, project_name: str) -> Path:
        """Get path to a project manifest."""
        return self.manifests_dir / f"{project_name}.json"
    
    def backup_dir(self, project_name: str) -> Path:
        """Get path to a project's backup directory."""
        return self.backups_dir / project_name
    
    def backup_path(self, project_name: str, date: Optional[datetime] = None) -> Path:
        """Get path to a timestamped backup."""
        if date is None:
            date = datetime.now()
        timestamp = date.strftime("%Y-%m-%d")
        backup_dir = self.backup_dir(project_name)
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir / f"{timestamp}.json"
    
    def language_actions_path(self, language: str) -> Path:
        """Get path to language-specific actions file."""
        return self.language_actions_dir / f"{language}.yaml"


# manifest.py
# ============================================================================

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
        commands: List[str],
    ):
        self.name = name
        self.description = description
        self.language = language
        self.path = path  # Will be expanded by to_dict() if needed
        self.license = license
        self.gitignore = gitignore
        self.commands = commands
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectManifest":
        """Create manifest from dictionary (loaded from JSON)."""
        return cls(
            name=data["name"],
            description=data["description"],
            language=data["language"],
            path=data["path"],
            license=data["license"],
            gitignore=data.get("gitignore", []),
            commands=data.get("commands", []),
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
            "commands": self.commands,
        }
    
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


# prompts.py
# ============================================================================

class PromptHelper:
    """Simple, homegrown prompt helpers (no external dependencies)."""
    
    @staticmethod
    def text(prompt: str, default: str = "") -> str:
        """Prompt for text input."""
        full_prompt = f"{prompt}"
        if default:
            full_prompt += f" [{default}]"
        full_prompt += ": "
        
        result = input(full_prompt).strip()
        return result if result else default
    
    @staticmethod
    def yes_no(prompt: str, default: bool = False) -> bool:
        """Prompt for yes/no."""
        suffix = " [Y/n]" if default else " [y/N]"
        while True:
            result = input(prompt + suffix + ": ").strip().lower()
            if result in ("y", "yes"):
                return True
            elif result in ("n", "no"):
                return False
            elif not result:
                return default
            print("Please answer 'y' or 'n'.")
    
    @staticmethod
    def choice(prompt: str, options: List[str]) -> int:
        """Prompt for single selection from list (returns 0-indexed)."""
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                result = int(input("Selection: ").strip())
                if 1 <= result <= len(options):
                    return result - 1
                print(f"Please select 1-{len(options)}.")
            except ValueError:
                print("Please enter a number.")
    
    @staticmethod
    def multi_choice(prompt: str, options: List[str]) -> List[int]:
        """Prompt for multiple selections (returns 0-indexed list)."""
        print(f"\n{prompt}")
        selected = [False] * len(options)
        
        while True:
            for i, option in enumerate(options):
                marker = "[x]" if selected[i] else "[ ]"
                print(f"{i+1}. {marker} {option}")
            
            print("\nEnter number to toggle, or 'done' to finish:")
            result = input("> ").strip().lower()
            
            if result == "done":
                return [i for i, s in enumerate(selected) if s]
            
            try:
                idx = int(result) - 1
                if 0 <= idx < len(options):
                    selected[idx] = not selected[idx]
                else:
                    print(f"Please select 1-{len(options)}.")
            except ValueError:
                print("Please enter a number or 'done'.")


# commands.py
# ============================================================================

class CommandLibrary:
    """Manages the command library."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.commands = self._load_commands()
    
    def _load_commands(self) -> Dict[str, Dict[str, str]]:
        """Load commands from commands.json."""
        if not self.config.commands_file.exists():
            return self._default_commands()
        
        return json.loads(self.config.commands_file.read_text())
    
    def _default_commands(self) -> Dict[str, Dict[str, str]]:
        """Default commands if file doesn't exist."""
        return {
            "commands": [
                {
                    "id": "venv",
                    "name": "Create virtual environment",
                    "command": "python3 -m venv .venv",
                },
                {
                    "id": "activate",
                    "name": "Activate venv",
                    "command": "source .venv/bin/activate",
                },
                {
                    "id": "git_init",
                    "name": "Initialize git",
                    "command": "git init",
                },
                {
                    "id": "git_commit",
                    "name": "Initial commit",
                    "command": 'git add . && git commit -m "Initial project scaffold"',
                },
                {
                    "id": "codium",
                    "name": "Launch Codium",
                    "command": "codium .",
                },
                {
                    "id": "pytest",
                    "name": "Run pytest",
                    "command": "pytest",
                },
            ]
        }
    
    def get_all(self) -> List[Dict[str, str]]:
        """Get all available commands."""
        return self.commands.get("commands", [])
    
    def get_by_id(self, cmd_id: str) -> Optional[Dict[str, str]]:
        """Get a command by ID."""
        for cmd in self.get_all():
            if cmd["id"] == cmd_id:
                return cmd
        return None


# language_actions.py
# ============================================================================

import yaml

class LanguageActions:
    """Loads and manages language-specific actions."""
    
    def __init__(self, config_manager: ConfigManager, language: str):
        self.config = config_manager
        self.language = language
        self.actions = self._load_actions()
    
    def _load_actions(self) -> List[Dict[str, Any]]:
        """Load language-specific actions from YAML."""
        path = self.config.language_actions_path(self.language)
        
        if not path.exists():
            return []
        
        data = yaml.safe_load(path.read_text())
        return data.get("actions", []) if data else []
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all actions for this language."""
        return self.actions


# tmux.py
# ============================================================================

import subprocess

class TMuxSession:
    """Manages tmux session creation and attachment."""
    
    def __init__(self, session_name: str):
        self.session_name = session_name
    
    def session_exists(self) -> bool:
        """Check if session already exists."""
        try:
            subprocess.run(
                ["tmux", "has-session", "-t", self.session_name],
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create(self) -> None:
        """Create a new tmux session (does nothing if already exists)."""
        if not self.session_exists():
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", self.session_name],
                check=True,
            )
    
    def send_command(self, command: str) -> None:
        """Send a command to the session."""
        subprocess.run(
            ["tmux", "send-keys", "-t", self.session_name, command, "Enter"],
            check=True,
        )
    
    def attach(self) -> None:
        """Attach to the session (blocks until user exits)."""
        subprocess.run(
            ["tmux", "attach-session", "-t", self.session_name],
        )


# ============================================================================
# End of module structure
# ============================================================================
