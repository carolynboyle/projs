"""
projs.gui.theme - Theme manager for the projs GUI.

Loads theme configuration from the active theme directory and exposes
colors, fonts, and icons to the rest of the GUI. Falls back to the
default theme for any missing values.
"""

from pathlib import Path
import yaml
import ttkbootstrap as ttk

_THEMES_DIR = Path(__file__).parent.parent / "data" / "themes"
_DEFAULT_THEME = "default"


class ThemeManager:
    """
    Loads and exposes the active theme.

    Usage:
        theme = ThemeManager(config)
        window = ttk.Window(themename=theme.ttkbootstrap_theme)
        color = theme.get("accent_color")
        icon  = theme.icon("dashboard")
    """

    def __init__(self, config):
        self.config = config
        self._data = {}
        self._icons = {}
        self._theme_dir = None
        self._load()

    def _load(self):
        """Load the active theme, falling back to default for missing values."""
        active = self.config.system.get("theme", _DEFAULT_THEME)
        theme_dir = _THEMES_DIR / active

        if not theme_dir.exists():
            print(f"Warning: theme '{active}' not found, using default.")
            theme_dir = _THEMES_DIR / _DEFAULT_THEME

        self._theme_dir = theme_dir
        theme_file = theme_dir / "theme.yaml"

        if not theme_file.exists():
            raise FileNotFoundError(f"theme.yaml not found in {theme_dir}")

        with theme_file.open() as f:
            self._data = yaml.safe_load(f) or {}

        # Merge with default so missing keys always fall back gracefully
        if active != _DEFAULT_THEME:
            default_file = _THEMES_DIR / _DEFAULT_THEME / "theme.yaml"
            if default_file.exists():
                with default_file.open() as f:
                    defaults = yaml.safe_load(f) or {}
                merged = defaults.copy()
                merged.update(self._data)
                self._data = merged

    def get(self, key: str, fallback=None):
        """Get a theme value by key."""
        return self._data.get(key, fallback)

    @property
    def ttkbootstrap_theme(self) -> str:
        """The ttkbootstrap theme name to pass to ttk.Window."""
        return self._data.get("ttkbootstrap_theme", "litera")

    @property
    def font_family(self) -> str:
        """Font family docstring"""
        return self._data.get("font_family", "TkDefaultFont")

    @property
    def font_size(self) -> int:
        """Font Size docstring"""
        return self._data.get("font_size", 11)

    @property
    def header_font(self) -> tuple:
        """Font tuple for the app header/logo text."""
        return (
            self._data.get("header_font_family", self.font_family),
            self._data.get("header_font_size", 24),
        )

    @property
    def name(self) -> str:
        """docstring to make the linter happy"""
        return self._data.get("name", "Default")

    def icon(self, name: str):
        """
        Get a loaded PhotoImage by icon name.
        Returns None if the icon is not defined or file is missing.
        Caches loaded images to avoid garbage collection.
        """
        if name in self._icons:
            return self._icons[name]

        icons_data = self._data.get("icons", {})
        rel_path = icons_data.get(name)
        if not rel_path:
            return None

        icon_path = self._theme_dir / rel_path
        if not icon_path.exists():
            print(f"Warning: icon '{name}' not found at {icon_path}")
            return None

        try:
            img = ttk.PhotoImage(file=str(icon_path))
            self._icons[name] = img  # hold reference — PhotoImage gets GC'd otherwise
            return img
        except Exception:  # pylint: disable=broad-except
            print(f"Warning: could not load icon '{name}' from {icon_path}")
            return None

    def available_themes(self) -> list:
        """Return list of all installed theme names."""
        if not _THEMES_DIR.exists():
            return [_DEFAULT_THEME]
        return [d.name for d in _THEMES_DIR.iterdir() if d.is_dir()]
