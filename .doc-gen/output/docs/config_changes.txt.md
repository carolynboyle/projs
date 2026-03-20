# config_changes.txt

**Path:** docs/config_changes.txt
**Syntax:** text
**Generated:** 2026-03-19 14:56:23

```text
# Changes required in config.py
# Two additions only — everything else stays identical.

# 1. In __init__, add drafts_dir alongside the other dirs:
self.drafts_dir = self.root / "drafts"

# 2. In _ensure_dirs(), add drafts_dir to the list:
self.drafts_dir,

```
