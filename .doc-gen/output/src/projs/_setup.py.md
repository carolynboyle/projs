# _setup.py

**Path:** src/projs/_setup.py
**Syntax:** python
**Generated:** 2026-03-21 11:14:03

```python
"""
projs._setup - First-run initialization

Copies shipped defaults from projs/data/ into ~/.projects/ and
prompts for any settings that can't be auto-detected.
"""

import sys
import platform
import shutil
from pathlib import Path
import yaml


# Path to shipped defaults, relative to this file
_DATA_DIR = Path(__file__).parent / "data"


def detect_package_manager() -> str:
    """
    Auto-detect the system package manager.

    Reads detection rules from platforms.yaml rather than hardcoding them.
    Falls back to 'unknown' if nothing matches.
    """
    platforms_file = _DATA_DIR / "platforms.yaml"
    if not platforms_file.exists():
        print("Warning: platforms.yaml not found, package manager set to 'unknown'")
        return "unknown"

    try:
        data = yaml.safe_load(platforms_file.read_text())
    except Exception as e:
        print(f"Warning: could not load platforms.yaml: {e}")
        return "unknown"

    system = platform.system().lower()  # 'linux', 'darwin', 'windows'

    platform_data = data.get(system)
    if not platform_data:
        return data.get("other", {}).get("default", "unknown")

    # Run through detectors (Linux only — others just use default)
    for detector in platform_data.get("detectors", []):
        if Path(detector["file"]).exists():
            return detector["manager"]

    return platform_data.get("default", "unknown")


def prompt_editor(config_dir: Path) -> str:
    """
    Prompt user to select their preferred editor from editor_menu options.

    Reads editor list from menus.yaml rather than hardcoding it.
    """
    menus_file = config_dir / "menus.yaml"
    if not menus_file.exists():
        menus_file = _DATA_DIR / "menus.yaml"

    editors = []
    try:
        data = yaml.safe_load(menus_file.read_text())
        items = data.get("editor_menu", {}).get("items", [])
        # Exclude 'back' and 'custom_editor' from the auto-list
        editors = [
            item for item in items
            if item["id"] not in ("back", "custom_editor")
        ]
    except Exception as e:
        print(f"Warning: could not load editor list: {e}")

    print("\n-- Select your preferred editor --")
    for i, item in enumerate(editors, 1):
        print(f"{i}. {item['display']}")
    print(f"{len(editors) + 1}. Enter custom command")

    while True:
        try:
            choice = int(input("Selection: ").strip())
            if 1 <= choice <= len(editors):
                return editors[choice - 1]["id"]
            elif choice == len(editors) + 1:
                custom = input("Editor command: ").strip()
                if custom:
                    return custom
                print("Editor command cannot be empty.")
            else:
                print(f"Please select 1-{len(editors) + 1}.")
        except ValueError:
            print("Please enter a number.")


def prompt_author() -> str:
    """Prompt for the author name used in generated LICENSE files."""
    print("\n-- Author name for LICENSE files --")
    print("This will be used in the copyright line of generated LICENSE files.")
    print("Example: Jane Smith")
    while True:
        author = input("Author name: ").strip()
        if author:
            return author
        print("Author name cannot be empty.")


def copy_defaults(root: Path) -> None:
    """
    Copy shipped data files into ~/.projects/ on first run.

    User files in ~/.projects/ are never overwritten if they already exist.
    """
    config_dir = root / "config"

    copies = [
        (_DATA_DIR / "defaults.yaml",  config_dir / "defaults.yaml"),
        (_DATA_DIR / "menus.yaml",     config_dir / "menus.yaml"),
        (_DATA_DIR / "commands.json",  root / "commands.json"),
    ]

    for src, dst in copies:
        if dst.exists():
            continue  # never overwrite user files
        if not src.exists():
            print(f"Warning: shipped default not found: {src}")
            continue
        try:
            shutil.copy2(src, dst)
            print(f"✓ Created {dst}")
        except Exception as e:
            print(f"✗ Error copying {src} to {dst}: {e}", file=sys.stderr)

    # Copy language-actions defaults
    lang_actions_dst = root / "language-actions"
    lang_actions_src = _DATA_DIR / "language-actions"
    if lang_actions_src.exists():
        for src_file in lang_actions_src.glob("*.yaml"):
            dst_file = lang_actions_dst / src_file.name
            if dst_file.exists():
                continue
            try:
                shutil.copy2(src_file, dst_file)
                print(f"✓ Created {dst_file}")
            except Exception as e:
                print(f"✗ Error copying {src_file}: {e}", file=sys.stderr)


def create_system_yaml(root: Path, editor: str, pkg_mgr: str, author: str) -> None:
    """
    Write ~/.projects/system.yaml with detected/prompted values.

    Loads structure from shipped system.yaml so defaults stay in data files.
    """
    src = _DATA_DIR / "system.yaml"
    system_file = root / "system.yaml"

    try:
        data = yaml.safe_load(src.read_text()) if src.exists() else {}
    except Exception as e:
        print(f"Warning: could not load shipped system.yaml: {e}")
        data = {}

    data["editor"] = editor
    data["package_manager"] = pkg_mgr
    data["author"] = author

    try:
        system_file.write_text(yaml.dump(data, default_flow_style=False))
        print(f"✓ Created {system_file}")
        print(f"  Editor: {editor}")
        print(f"  Package manager: {pkg_mgr}")
        print(f"  Author: {author}")
    except Exception as e:
        print(f"✗ Error writing system.yaml: {e}", file=sys.stderr)


def initialize_projs() -> None:
    """Initialize projs on first run."""
    root = Path.home() / ".projects"

    # Create directory structure
    for d in [
        root / "manifests",
        root / "backups",
        root / "templates",
        root / "language-actions",
        root / "config",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy shipped defaults into ~/.projects/
    copy_defaults(root)

    # Auto-detect package manager
    pkg_mgr = detect_package_manager()

    # Prompt for editor and author
    editor = prompt_editor(root / "config")
    author = prompt_author()

    # Write system.yaml with real values
    create_system_yaml(root, editor, pkg_mgr, author)

    print(f"\n✓ projs initialized at {root}")
    print(f"  Edit {root / 'system.yaml'} to customize your preferences")


if __name__ == "__main__":
    initialize_projs()

```
