# __init__.py

**Path:** src/projs/__init__.py
**Syntax:** python
**Generated:** 2026-03-22 18:36:59

```python
"""
projs - Project launcher and setup manager

A CLI tool for creating, launching, and managing local development projects
with tmux session management and interactive configuration.
"""

__version__ = "0.1.0"
__author__ = "Frazzled"
__description__ = "Project launcher and setup manager for homelab"

from projs.cli.main import cli

__all__ = ["cli"]
```
