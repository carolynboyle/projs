# __init__.py

**Path:** src/projs/cli/__init__.py
**Syntax:** python
**Generated:** 2026-03-21 11:14:03

```python
"""projs.cli - Command-line interface for projs."""

from projs.cli.main import cli
from projs.cli.creator import ProjectCreator
from projs.cli.launcher import ProjectLauncher
from projs.cli.modifier import ProjectModifier
from projs.cli.prompts import PromptHelper
from projs.cli.menu_builder import MenuBuilder

__all__ = [
    "cli",
    "ProjectCreator",
    "ProjectLauncher", 
    "ProjectModifier",
    "PromptHelper",
    "MenuBuilder",
]

```
