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