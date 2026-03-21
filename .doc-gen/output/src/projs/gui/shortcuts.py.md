# shortcuts.py

**Path:** src/projs/gui/shortcuts.py
**Syntax:** python
**Generated:** 2026-03-21 11:14:03

```python
"""
projs.gui.shortcuts - Centralised Alt+key shortcut manager.

Usage
-----
Create one ShortcutManager in ProjsApp and pass it to every panel.

    sm = ShortcutManager(root_window)
    sm.register(btn, panel_id="dashboard", key="l", underline=0, callback=do_launch)

Underlines are hidden until the user holds Alt, mirroring standard
Windows / GTK mnemonic behaviour.  When a panel is deactivated its
shortcuts go dormant so Alt+key can never fire a hidden button.
"""

from __future__ import annotations
from typing import Callable


class _Shortcut:
    """Internal record for one registered shortcut."""

    __slots__ = ("widget", "panel_id", "key", "underline", "callback")

    def __init__(self, widget, panel_id: str, key: str,
                 underline: int, callback: Callable):
        self.widget = widget
        self.panel_id = panel_id
        self.key = key
        self.underline = underline
        self.callback = callback


class ShortcutManager:
    """
    Centralised registry for Alt+key shortcuts across all panels.

    Rules
    -----
    - Underlines are hidden by default; shown only while Alt is held.
    - Only shortcuts belonging to the *active* panel_id fire.
    - Global shortcuts (panel_id=None) always fire regardless of panel.
    """

    def __init__(self, root):
        self._root = root
        self._shortcuts: list[_Shortcut] = []
        self._active_panel: str | None = None

        root.bind("<Alt_L>",          self._on_alt_press,   add="+")
        root.bind("<Alt_R>",          self._on_alt_press,   add="+")
        root.bind("<KeyRelease-Alt_L>", self._on_alt_release, add="+")
        root.bind("<KeyRelease-Alt_R>", self._on_alt_release, add="+")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, widget, *, panel_id: str | None,
                 key: str, underline: int, callback: Callable) -> None:
        """
        Register a widget's Alt+key shortcut.

        Parameters
        ----------
        widget      : any tk/ttk widget with a ``configure`` method
        panel_id    : panel this shortcut belongs to, or None for global
        key         : single character, e.g. ``"l"`` for Alt+L
        underline   : character index to underline in the widget label
        callback    : callable invoked when the shortcut fires
        """
        sc = _Shortcut(widget, panel_id, key.lower(), underline, callback)
        self._shortcuts.append(sc)

        # Hide underline until Alt is pressed
        self._set_underline(sc, visible=False)

        # Bind the key; the handler checks active panel at fire time
        self._root.bind(
            f"<Alt-{key.lower()}>",
            lambda e, s=sc: self._fire(s),
            add="+",
        )

    def activate_panel(self, panel_id: str) -> None:
        """Mark *panel_id* as active so its shortcuts can fire."""
        self._active_panel = panel_id

    def unregister_panel(self, panel_id: str) -> None:
        """
        Remove all shortcuts registered under *panel_id*.

        Call this when a panel is destroyed (not just hidden — hidden
        panels should use activate_panel / deactivation instead).
        """
        self._shortcuts = [
            sc for sc in self._shortcuts if sc.panel_id != panel_id
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fire(self, sc: _Shortcut) -> None:
        """Invoke *sc* if its panel is currently active (or it's global)."""
        if sc.panel_id is None or sc.panel_id == self._active_panel:
            sc.callback()

    def _on_alt_press(self, _event) -> None:
        """Show underlines for active-panel and global shortcuts."""
        for sc in self._shortcuts:
            if sc.panel_id is None or sc.panel_id == self._active_panel:
                self._set_underline(sc, visible=True)

    def _on_alt_release(self, _event) -> None:
        """Hide all underlines."""
        for sc in self._shortcuts:
            self._set_underline(sc, visible=False)

    @staticmethod
    def _set_underline(sc: _Shortcut, *, visible: bool) -> None:
        """
        Toggle the underline on *sc*'s widget.

        ttk widgets use ``underline=N`` to show and ``underline=-1`` to
        hide.  We swallow AttributeError / TclError silently so that
        stub / label widgets that don't support underline don't crash.
        """
        try:
            sc.widget.configure(underline=sc.underline if visible else -1)
        except Exception:  # pylint: disable=broad-except
            pass

```
