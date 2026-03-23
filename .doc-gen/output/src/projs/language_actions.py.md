# language_actions.py

**Path:** src/projs/language_actions.py
**Syntax:** python
**Generated:** 2026-03-22 18:36:59

```python
"""
projs.language_actions - Language-specific actions management
"""

from typing import List, Dict, Any

import yaml

from projs.config import ConfigManager


class LanguageActions:
    """Loads and manages language-specific actions."""

    def __init__(self, config_manager: ConfigManager, language: str):
        self.config = config_manager
        self.language = language
        self.actions = self._load_actions()

    def _load_actions(self) -> List[Dict[str, Any]]:
        """
        Load language-specific actions.

        Tries user path (~/.projects/language-actions/) first,
        falls back to shipped defaults in projs/data/language-actions/.
        """
        for path in (
            self.config.language_actions_path(self.language),
            self.config.default_language_actions_path(self.language),
        ):
            if path.exists():
                try:
                    data = yaml.safe_load(path.read_text())
                    if data:
                        return data.get("actions", [])
                except Exception as e:
                    print(f"Warning: could not load {path}: {e}")

        return []

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all actions for this language."""
        return self.actions

```
