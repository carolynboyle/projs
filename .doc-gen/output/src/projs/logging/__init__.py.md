# __init__.py

**Path:** src/projs/logging/__init__.py
**Syntax:** python
**Generated:** 2026-03-22 18:36:59

```python
"""
projs.logging - Unified logging for projects CLI and GUI.

Combines foundation (init, filtering), writers (file I/O, public API),
and rotation (daily log management) via mixins.

Usage:
    from projs.logging import ProjectsLogger

    logger = ProjectsLogger(config_manager)
    logger.info("Project created", project="myproject")
    logger.error("Something broke", project="myproject")
    logger.debug("Debug info", project="myproject")
"""

from projs.logging._foundation import _LoggerFoundation
from projs.logging._writers import _LoggerWriters
from projs.logging._rotation import _LoggerRotation


class ProjectsLogger(_LoggerFoundation, _LoggerWriters, _LoggerRotation):
    """
    Complete project logger with all functionality.

    Inherits from:
    - _LoggerFoundation: __init__, _should_log, _format_message
    - _LoggerWriters: _write_to_file, debug, info, error
    - _LoggerRotation: _rotate_if_needed, error_with_traceback

    Supports three log levels (configurable in system.yaml):
      - debug: verbose output for troubleshooting
      - info:  normal operation (default)
      - error: only failures

    Logs are written to:
      - User local: ~/.projects/logs/projs.log + per-project logs
      - Global: /opt/venvs/tools/logs/projs.log (or package fallback)
      - Per-project: ~/.projects/logs/projects/<name>/{debug,info,error}.log
    """
    pass


__all__ = ["ProjectsLogger"]
```
