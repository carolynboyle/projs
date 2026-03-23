# config.py

**Path:** src/projs/config.py
**Syntax:** python
**Generated:** 2026-03-22 18:36:59

```python
"""
projs.config - Configuration management

Loads user config from ~/.projects/config/.
Falls back to shipped defaults in projs/data/.
No hardcoded constants.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import yaml


# Path to shipped defaults, relative to this file
_DATA_DIR = Path(__file__).parent / "data"


class ConfigManager:
    """Manages ~/.projects/ directory structure, paths, and configuration."""

    def __init__(self, config_root: Optional[Path] = None):
        """Initialize config manager with root directory."""
        self.root = config_root or (Path.home() / ".projects")
        self.drafts_dir = self.root / "drafts"
        self.manifests_dir = self.root / "manifests"
        self.backups_dir = self.root / "backups"
        self.templates_dir = self.root / "templates"
        self.language_actions_dir = self.root / "language-actions"
        self.config_dir = self.root / "config"

        self.commands_file = self.root / "commands.json"
        self.system_file = self.root / "system.yaml"
        self.defaults_file = self.config_dir / "defaults.yaml"
        self.menus_file = self.config_dir / "menus.yaml"

        self._ensure_dirs()

        self.defaults = self._load_yaml(
            user_path=self.defaults_file,
            data_path=_DATA_DIR / "defaults.yaml",
        )
        self.system = self._load_yaml(
            user_path=self.system_file,
            data_path=_DATA_DIR / "system.yaml",
        )
        self.menus = self._load_yaml(
            user_path=self.menus_file,
            data_path=_DATA_DIR / "menus.yaml",
        )

    def _ensure_dirs(self):
        """Create all necessary directories if they don't exist."""
        for dir_path in [
            self.root,
            self.drafts_dir,
            self.manifests_dir,
            self.backups_dir,
            self.templates_dir,
            self.language_actions_dir,
            self.config_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _load_yaml(self, user_path: Path, data_path: Path) -> Dict[str, Any]:
        """
        Load a YAML config file.

        Tries user_path first, falls back to data_path (shipped defaults).
        Returns empty dict if neither exists.
        """
        for path in (user_path, data_path):
            if path.exists():
                try:
                    data = yaml.safe_load(path.read_text())
                    if data:
                        return data
                except (yaml.YAMLError, OSError) as e:
                    print(f"Warning: could not load {path}: {e}")

        print(f"Warning: no config found at {user_path} or {data_path}")
        return {}

    def save_system(self, config: Dict[str, Any]) -> None:
        """Save system configuration to system.yaml."""
        try:
            self.system_file.write_text(yaml.dump(config, default_flow_style=False))
            self.system = config
        except OSError as e:
            print(f"Error saving system config: {e}")

    # -- Convenience accessors ------------------------------------------------

    def get_licenses(self) -> list:
        """Get list of available licenses."""
        return self.defaults.get("licenses", [])

    def get_languages(self) -> list:
        """Get list of supported languages."""
        return self.defaults.get("languages", [])

    def get_gitignore(self, language: str) -> list:
        """Get gitignore template for a language."""
        return self.defaults.get("gitignore", {}).get(language, [])

    def get_editor(self) -> str:
        """Get preferred editor."""
        return self.system.get("editor", "")

    def get_editors(self) -> list:
        """Get list of known editors."""
        return self.defaults.get("editors", [])

    def get_launch_mode(self) -> str:
        """Get launch mode: 'standard' or 'debug'."""
        return self.system.get("launch_mode", "standard")

    def get_author(self) -> str:
        """Get author name for LICENSE files."""
        return self.system.get("author", "")

    def set_editor(self, editor: str) -> None:
        """Save editor preference to system.yaml."""
        self.system["editor"] = editor
        self.save_system(self.system)

    def set_launch_mode(self, mode: str) -> None:
        """Save launch mode to system.yaml."""
        self.system["launch_mode"] = mode
        self.save_system(self.system)

    def set_author(self, author: str) -> None:
        """Save author name to system.yaml."""
        self.system["author"] = author
        self.save_system(self.system)

    def get_package_manager(self) -> str:
        """Get package manager."""
        return self.system.get("package_manager", "unknown")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value."""
        return self.system.get("preferences", {}).get(key, default)

    def get_license_template(self, license_id: str) -> Optional[str]:
        """
        Load a license template from data/licenses/.

        Returns the template text with {year} and {author} placeholders,
        or None if no template exists for the given license id.
        """
        template_path = _DATA_DIR / "licenses" / f"{license_id}.txt"
        if template_path.exists():
            try:
                return template_path.read_text()
            except OSError as e:
                print(f"Warning: could not load license template {template_path}: {e}")
        return None

    # -- Path helpers ---------------------------------------------------------

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
        """Get path to language-specific actions file in ~/.projects/."""
        return self.language_actions_dir / f"{language}.yaml"

    def default_language_actions_path(self, language: str) -> Path:
        """Get path to shipped default language actions in projs/data/."""
        return _DATA_DIR / "language-actions" / f"{language}.yaml"

```
