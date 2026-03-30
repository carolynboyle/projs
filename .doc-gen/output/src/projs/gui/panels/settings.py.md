# settings.py

**Path:** src/projs/gui/panels/settings.py
**Syntax:** python
**Generated:** 2026-03-25 09:30:03

```python
"""
projs.gui.panels.settings - Application settings panel.

Sections
--------
  Default Editor   — combobox from editors list in defaults.yaml,
                     custom entry appears when "custom" is selected
  Launch Mode      — Standard (fire and attach) or Debug (log + manual Go)

Saves to ~/.projects/system.yaml via ConfigManager.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # pylint: disable=wildcard-import,unused-wildcard-import

from projs.config import ConfigManager
from projs.manifest import ManifestStore
from projs.gui.theme import ThemeManager
from projs.gui.shortcuts import ShortcutManager

_PANEL_ID = "settings"


class SettingsPanel(ttk.Frame):
    """Application settings panel."""

    def __init__(
        self,
        master,
        theme: ThemeManager,
        config: ConfigManager,
        manifest_store: ManifestStore,
        shortcuts: ShortcutManager,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.config = config
        self.manifest_store = manifest_store
        self.shortcuts = shortcuts

        self._editor_var = ttk.StringVar()
        self._custom_editor_var = ttk.StringVar()
        self._launch_mode_var = ttk.StringVar()
        self._status_var = ttk.StringVar()

        self._build()
        self._load()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self):
        self.columnconfigure(0, weight=1)

        # Title
        ttk.Label(
            self,
            text="Settings",
            font=(self.theme.font_family, 16),
        ).grid(row=0, column=0, sticky=W, padx=24, pady=(20, 4))

        ttk.Separator(self, orient=HORIZONTAL).grid(
            row=1, column=0, sticky=EW, padx=24, pady=(0, 16)
        )

        # Content frame — two sections
        content = ttk.Frame(self, padding=(24, 0))
        content.grid(row=2, column=0, sticky=NSEW)
        content.columnconfigure(1, weight=1)

        row = 0

        # ── Default Editor ────────────────────────────────────────────
        ttk.Label(
            content,
            text="Default Editor",
            font=(self.theme.font_family, 11, "bold"),
        ).grid(row=row, column=0, columnspan=2, sticky=W, pady=(0, 6))
        row += 1

        ttk.Label(content, text="Editor").grid(
            row=row, column=0, sticky=W, padx=(0, 16), pady=4
        )
        editors = self.config.get_editors()
        self._editor_cb = ttk.Combobox(
            content,
            textvariable=self._editor_var,
            values=editors,
            state="readonly",
            width=20,
        )
        self._editor_cb.grid(row=row, column=1, sticky=W, pady=4)
        self._editor_var.trace_add("write", self._on_editor_change)
        row += 1

        # Custom editor entry — hidden unless "custom" selected
        self._custom_label = ttk.Label(content, text="Command")
        self._custom_label.grid(row=row, column=0, sticky=W, padx=(0, 16), pady=4)
        self._custom_entry = ttk.Entry(
            content,
            textvariable=self._custom_editor_var,
            width=24,
        )
        self._custom_entry.grid(row=row, column=1, sticky=W, pady=4)
        self._custom_row = row
        row += 1

        ttk.Label(
            content,
            text="Used when no per-project editor is set.",
            font=(self.theme.font_family, 9),
            bootstyle=SECONDARY,
        ).grid(row=row, column=1, sticky=W, pady=(0, 16))
        row += 1

        ttk.Separator(content, orient=HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=EW, pady=(0, 16)
        )
        row += 1

        # ── Launch Mode ───────────────────────────────────────────────
        ttk.Label(
            content,
            text="Launch Mode",
            font=(self.theme.font_family, 11, "bold"),
        ).grid(row=row, column=0, columnspan=2, sticky=W, pady=(0, 6))
        row += 1

        for value, label, sublabel in [
            (
                "standard",
                "Standard",
                "Fire commands and attach to tmux session immediately.",
            ),
            (
                "debug",
                "Debug",
                "Show command log, wait for manual Go. Logs saved to ~/.projects/logs/.",
            ),
        ]:
            rb = ttk.Radiobutton(
                content,
                text=label,
                variable=self._launch_mode_var,
                value=value,
                bootstyle=PRIMARY,
            )
            rb.grid(row=row, column=0, columnspan=2, sticky=W, pady=(2, 0))
            row += 1
            ttk.Label(
                content,
                text=sublabel,
                font=(self.theme.font_family, 9),
                bootstyle=SECONDARY,
            ).grid(row=row, column=0, columnspan=2, sticky=W, padx=(24, 0), pady=(0, 8))
            row += 1

        ttk.Separator(content, orient=HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=EW, pady=(0, 16)
        )
        row += 1

        # ── Save button + status ──────────────────────────────────────
        btn_row = ttk.Frame(content)
        btn_row.grid(row=row, column=0, columnspan=2, sticky=W)

        ttk.Button(
            btn_row,
            text="Save",
            bootstyle=SUCCESS,
            command=self._do_save,
        ).pack(side=LEFT)

        ttk.Label(
            btn_row,
            textvariable=self._status_var,
            font=(self.theme.font_family, 9),
            bootstyle=SUCCESS,
        ).pack(side=LEFT, padx=(12, 0))

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------

    def _load(self):
        """Populate fields from current config."""
        editors = self.config.get_editors()
        current_editor = self.config.get_editor()

        if current_editor in editors:
            self._editor_var.set(current_editor)
        elif current_editor:
            # Editor is set but not in the known list — show as custom
            self._editor_var.set("custom")
            self._custom_editor_var.set(current_editor)
        elif editors:
            self._editor_cb.current(0)

        self._launch_mode_var.set(self.config.get_launch_mode())
        self._update_custom_visibility()

    def _do_save(self):
        """Write settings back to system.yaml."""
        editor = self._editor_var.get()
        if editor == "custom":
            editor = self._custom_editor_var.get().strip()
            if not editor:
                self._status_var.set("⚠ Enter a custom editor command.")
                return

        launch_mode = self._launch_mode_var.get()

        self.config.set_editor(editor)
        self.config.set_launch_mode(launch_mode)

        self._status_var.set("✓ Saved.")
        # Clear the status message after 3 seconds
        self.after(3000, lambda: self._status_var.set(""))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _on_editor_change(self, *_):
        self._update_custom_visibility()
        self._status_var.set("")

    def _update_custom_visibility(self):
        """Show or hide the custom editor entry row."""
        if self._editor_var.get() == "custom":
            self._custom_label.grid()
            self._custom_entry.grid()
        else:
            self._custom_label.grid_remove()
            self._custom_entry.grid_remove()

    def refresh(self):
        """Reload from config (called when panel is raised)."""
        self._load()
        self._status_var.set("")

```
