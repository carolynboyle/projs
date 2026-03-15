"""
projs.tmux - Tmux session management
"""

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
