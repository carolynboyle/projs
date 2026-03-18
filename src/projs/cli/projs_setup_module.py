"""
projs._setup - Installation-time setup and initialization

This module runs automatically when projs is installed via pip.
It initializes the ~/.projects/ directory structure and creates all
necessary config files.
"""

import sys
import platform
from pathlib import Path
import json
import yaml


def detect_package_manager():
    """Auto-detect the system package manager."""
    system = platform.system()
    
    if system == "Linux":
        # Check which distro we're on
        distro_checks = [
            ("/etc/fedora-release", "dnf"),
            ("/etc/redhat-release", "dnf"),
            ("/etc/debian_version", "apt"),
            ("/etc/arch-release", "pacman"),
            ("/etc/gentoo-release", "emerge"),
        ]
        
        for file_path, pkg_mgr in distro_checks:
            if Path(file_path).exists():
                return pkg_mgr
        
        return "apt"  # Default to apt for unknown Linux
    
    elif system == "Darwin":
        return "brew"
    
    elif system == "Windows":
        return "choco"  # Assuming Chocolatey on Windows
    
    return "other"


def create_defaults_yaml(config_dir: Path):
    """Create the defaults.yaml file."""
    defaults = {
        "licenses": [
            "MIT",
            "GPL v3",
            "Apache 2.0",
            "BSD 3-Clause",
            "ISC",
            "Custom/Other",
        ],
        "languages": [
            "python",
            "flutter",
            "bash",
            "other",
        ],
        "gitignore": {
            "python": [
                ".venv/",
                "__pycache__/",
                "*.pyc",
                ".env",
                "dist/",
                "build/",
                "*.egg-info/",
            ],
            "flutter": [
                ".dart_tool/",
                ".flutter-plugins",
                ".flutter-plugins-dependencies",
                ".packages",
                "build/",
            ],
            "bash": [
                ".env",
                "*.swp",
                "*.swo",
            ],
        },
    }
    
    defaults_file = config_dir / "defaults.yaml"
    defaults_file.write_text(yaml.dump(defaults, default_flow_style=False, sort_keys=False))
    return defaults_file


def create_system_yaml(root: Path, pkg_mgr: str):
    """Create the system.yaml file with detected package manager."""
    system_config = {
        "editor": "nano",
        "ide": "codium",
        "package_manager": pkg_mgr,
        "preferences": {
            "clear_screen_on_menu": True,
            "show_confirmations": True,
        },
    }
    
    system_file = root / "system.yaml"
    system_file.write_text(yaml.dump(system_config, default_flow_style=False, sort_keys=False))
    return system_file


def create_commands_json(root: Path):
    """Create the initial commands.json file."""
    commands = {
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
    
    commands_file = root / "commands.json"
    commands_file.write_text(json.dumps(commands, indent=2))
    return commands_file


def initialize_projs():
    """Initialize projs on first install."""
    root = Path.home() / ".projects"
    
    # Create directory structure
    (root / "manifests").mkdir(parents=True, exist_ok=True)
    (root / "backups").mkdir(parents=True, exist_ok=True)
    (root / "templates").mkdir(parents=True, exist_ok=True)
    (root / "language-actions").mkdir(parents=True, exist_ok=True)
    config_dir = root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Detect package manager
    pkg_mgr = detect_package_manager()
    
    # Create config files
    try:
        defaults_file = create_defaults_yaml(config_dir)
        print(f"✓ Created {defaults_file}")
    except Exception as e:
        print(f"✗ Error creating defaults.yaml: {e}", file=sys.stderr)
    
    try:
        system_file = create_system_yaml(root, pkg_mgr)
        print(f"✓ Created {system_file}")
        print(f"  Detected package manager: {pkg_mgr}")
    except Exception as e:
        print(f"✗ Error creating system.yaml: {e}", file=sys.stderr)
    
    try:
        commands_file = create_commands_json(root)
        print(f"✓ Created {commands_file}")
    except Exception as e:
        print(f"✗ Error creating commands.json: {e}", file=sys.stderr)
    
    print(f"\n✓ projs initialized at {root}")
    print(f"  Edit {root / 'system.yaml'} to customize your preferences")


if __name__ == "__main__":
    initialize_projs()
