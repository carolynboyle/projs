# app.py

**Path:** src/projs/gui/app.py
**Syntax:** python
**Generated:** 2026-03-19 14:56:23

```python
"""
projs.gui.app - Main GUI window for projs.

Layout
------
  Row 0  Header bar  — logo · project breadcrumb · action buttons
  Row 1  Body        — sidebar (col 0) | main panel (col 1)
  Row 2  Status bar  — status · project count
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # pylint: disable=wildcard-import,unused-wildcard-import

from projs.config import ConfigManager
from projs.manifest import ManifestStore, ProjectManifest
from projs.gui.theme import ThemeManager
from projs.gui.shortcuts import ShortcutManager
from projs.gui.panels.dashboard import DashboardPanel
from projs.gui.panels.new_project import NewProjectPanel as _NewProjectPanel
from projs.gui.panels.settings import SettingsPanel as _SettingsPanel


class ProjsApp(ttk.Frame):
    """Main application frame."""

    def __init__(self, master, theme: ThemeManager, config: ConfigManager, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=BOTH, expand=YES)

        self.theme = theme
        self.config = config
        self.manifest_store = ManifestStore(config)
        self.shortcuts = ShortcutManager(master)

        # Header widget refs — populated in _build_header
        self._project_label: ttk.Label | None = None
        self._launch_btn: ttk.Button | None = None
        self._modify_btn: ttk.Button | None = None
        self._delete_btn: ttk.Button | None = None

        # Status bar refs
        self._status_var = ttk.StringVar(value="status: ready")
        self._count_var = ttk.StringVar(value="")

        # Panel registry
        self._main: ttk.Frame | None = None
        self._panels: dict = {}

        # Root grid weights
        self.columnconfigure(0, weight=0)  # sidebar — fixed width
        self.columnconfigure(1, weight=1)  # main panel — expands
        self.rowconfigure(0, weight=0)     # header — fixed height
        self.rowconfigure(1, weight=1)     # body — expands
        self.rowconfigure(2, weight=0)     # status bar — fixed height

        self._build_header()
        self._build_body()
        self._build_statusbar()

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _build_header(self):
        """Slim top bar: logo | project breadcrumb ··· action buttons."""
        hdr = ttk.Frame(self, padding=(10, 6), bootstyle=SECONDARY)
        hdr.grid(row=0, column=0, columnspan=2, sticky=EW)
        self._header = hdr
        hdr.columnconfigure(2, weight=1)   # spacer expands, pushing buttons left toward breadcrumb

        # Logo / app name
        logo_img = self.theme.icon("logo")
        if logo_img:
            ttk.Label(
                hdr,
                image=logo_img,
                bootstyle=(INVERSE, SECONDARY),
            ).grid(row=0, column=0, sticky=W)
        else:
            ttk.Label(
                hdr,
                text="$ projs_",
                font=(self.theme.font_family, self.theme.get("header_font_size", 16)),
                bootstyle=(INVERSE, SECONDARY),
            ).grid(row=0, column=0, sticky=W)

        # Project breadcrumb — updates when a project is selected
        self._project_label = ttk.Label(
            hdr,
            text="",
            font=(self.theme.font_family, 11),
            bootstyle=(INVERSE, SECONDARY),
        )
        self._project_label.grid(row=0, column=1, sticky=W, padx=(12, 0))

        # Action buttons — immediately after breadcrumb
        btn_frame = ttk.Frame(hdr, bootstyle=SECONDARY)
        btn_frame.grid(row=0, column=2, sticky=W, padx=(8, 0))

        self._launch_btn = ttk.Button(
            btn_frame, text="Launch", bootstyle=SUCCESS,
            state=DISABLED, command=self._do_launch,
        )
        self._launch_btn.pack(side=LEFT, padx=(0, 4))

        self._modify_btn = ttk.Button(
            btn_frame, text="Modify", bootstyle=INFO,
            state=DISABLED, command=self._do_modify,
        )
        self._modify_btn.pack(side=LEFT, padx=(0, 4))

        self._delete_btn = ttk.Button(
            btn_frame, text="Delete", bootstyle=DANGER,
            state=DISABLED, command=self._do_delete,
        )
        self._delete_btn.pack(side=LEFT)

        # Register header shortcuts (global — always active)
        self.shortcuts.register(
            self._launch_btn, panel_id=None,
            key="l", underline=0, callback=self._do_launch,
        )
        self.shortcuts.register(
            self._modify_btn, panel_id=None,
            key="f", underline=4, callback=self._do_modify,
        )
        self.shortcuts.register(
            self._delete_btn, panel_id=None,
            key="t", underline=4, callback=self._do_delete,
        )

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self):
        self._build_sidebar()
        self._build_main_panel()

    def _build_sidebar(self):
        """Left nav sidebar."""
        sidebar = ttk.Frame(self, padding=0)
        sidebar.grid(row=1, column=0, sticky=NSEW)

        buttons = [
            ("dashboard",    "dashboard",      0, self._show_dashboard),
            ("new_project",  "create/import",  0, self._show_new_project),
            ("settings",     "settings",       0, self._show_settings),
            ("help",         "help",           0, self._show_help),
        ]
        keys = ["d", "c", "s", "h"]

        for (icon_name, label, ul, command), key in zip(buttons, keys):
            img = self.theme.icon(icon_name)
            btn = ttk.Button(
                sidebar,
                image=img if img else None,
                text=label,
                compound=TOP if img else None,
                command=command,
                bootstyle=INFO,
            )
            btn.pack(side=TOP, fill=BOTH, ipadx=10, ipady=10)
            self.shortcuts.register(
                btn, panel_id=None,
                key=key, underline=ul, callback=command,
            )

    def _build_main_panel(self):
        """Stacked panels — only the active one is raised."""
        self._main = ttk.Frame(self)
        self._main.grid(row=1, column=1, sticky=NSEW)
        self._main.columnconfigure(0, weight=1)
        self._main.rowconfigure(0, weight=1)

        panel_defs = [
            ("dashboard",   DashboardPanel,  {"on_select": self._on_project_selected,
                                               "on_create": self._show_new_project}),
            ("new_project", NewProjectPanel, {}),
            ("settings",    SettingsPanel,   {}),
            ("help",        HelpPanel,       {}),
        ]

        for name, cls, kwargs in panel_defs:
            panel = cls(
                self._main, self.theme, self.config,
                self.manifest_store, self.shortcuts, **kwargs,
            )
            panel.grid(row=0, column=0, sticky=NSEW)
            self._panels[name] = panel

        self._show_dashboard()

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------

    def _build_statusbar(self):
        """Pinned footer — status message and project count."""
        bar = ttk.Frame(self, padding=(10, 3), bootstyle=SECONDARY)
        bar.grid(row=2, column=0, columnspan=2, sticky=EW)
        bar.columnconfigure(1, weight=1)

        ttk.Label(
            bar,
            textvariable=self._status_var,
            font=(self.theme.font_family, 9),
            bootstyle=(INVERSE, SECONDARY),
        ).grid(row=0, column=0, sticky=W)

        ttk.Label(
            bar,
            textvariable=self._count_var,
            font=(self.theme.font_family, 9),
            bootstyle=(INVERSE, SECONDARY),
        ).grid(row=0, column=1, sticky=E)

    def update_status(self, message: str = "ready", project_count: int | None = None):
        """Update the status bar text and optional project count."""
        self._status_var.set(f"status: {message}")
        if project_count is not None:
            noun = "project" if project_count == 1 else "projects"
            self._count_var.set(f"{project_count} {noun}")

    # ------------------------------------------------------------------
    # Panel switching
    # ------------------------------------------------------------------

    def _show_panel(self, name: str):
        self._panels[name].tkraise()
        self.shortcuts.activate_panel(name)

    def _show_dashboard(self):
        self._header.grid()
        panel = self._panels["dashboard"]
        panel.refresh()
        self._show_panel("dashboard")

    def _show_new_project(self):
        self._on_project_selected(None)   # clear breadcrumb + disable action buttons
        self._header.grid_remove()
        self._panels["new_project"].reset()
        self._show_panel("new_project")

    def _show_settings(self):
        self._panels["settings"].refresh()
        self._show_panel("settings")

    def _show_help(self):
        self._show_panel("help")

    # ------------------------------------------------------------------
    # Project selection callback — called by DashboardPanel
    # ------------------------------------------------------------------

    def _on_project_selected(self, manifest: ProjectManifest | None):
        """Update header breadcrumb and action button states."""
        if manifest is None:
            self._project_label.configure(text="")
            for btn in (self._launch_btn, self._modify_btn, self._delete_btn):
                btn.configure(state=DISABLED)
        else:
            tag = f"[{manifest.language} · local]"
            self._project_label.configure(text=f"›  {manifest.name}  {tag}")
            for btn in (self._launch_btn, self._modify_btn, self._delete_btn):
                btn.configure(state=NORMAL)

        # Keep project count fresh
        count = len(self.manifest_store.list_all())
        self.update_status(project_count=count)

    # ------------------------------------------------------------------
    # Action button handlers (header buttons delegate to active panel)
    # ------------------------------------------------------------------

    def _on_new_project_done(self, manifest):
        """Called when NewProjectPanel successfully creates a project."""
        # Refresh dashboard and select the new project
        dash = self._panels.get("dashboard")
        if dash:
            dash.refresh()
            dash.select_project(manifest.name)
        self._show_dashboard()
        count = len(self.manifest_store.list_all())
        self.update_status(f"Project '{manifest.name}' created", project_count=count)

    def _do_launch(self):
        dash = self._panels.get("dashboard")
        if dash:
            dash.do_launch()

    def _do_modify(self):
        dash = self._panels.get("dashboard")
        if dash:
            dash.do_modify()

    def _do_delete(self):
        dash = self._panels.get("dashboard")
        if dash:
            dash.do_delete()


# ---------------------------------------------------------------------------
# Base panel
# ---------------------------------------------------------------------------

class _BasePanel(ttk.Frame):
    """Base class for all main panels."""

    def __init__(self, master, theme: ThemeManager, config: ConfigManager,
                 manifest_store: ManifestStore, shortcuts: ShortcutManager, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.config = config
        self.manifest_store = manifest_store
        self.shortcuts = shortcuts
        self._build()

    def _build(self):
        """Override in subclass to build panel contents."""

    def refresh(self):
        """Override to refresh dynamic content."""

    def reset(self):
        """Override to reset form state."""

    def do_launch(self):
        """Override in panels that support Launch."""

    def do_modify(self):
        """Override in panels that support Modify."""

    def do_delete(self):
        """Override in panels that support Delete."""


# ---------------------------------------------------------------------------
# Stub panels
# ---------------------------------------------------------------------------

class NewProjectPanel(_BasePanel):
    """Thin wrapper — delegates to the real wizard in panels/new_project.py."""

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._wizard = _NewProjectPanel(
            self,
            theme=self.theme,
            config=self.config,
            manifest_store=self.manifest_store,
            shortcuts=self.shortcuts,
            on_done=self._on_done,
            on_cancel=self._on_cancel,
        )
        self._wizard.grid(row=0, column=0, sticky=NSEW)

    def _on_done(self, manifest):
        """Project created — bubble up to app via master chain."""
        app = self._find_app()
        if app:
            app._on_new_project_done(manifest)

    def _on_cancel(self):
        app = self._find_app()
        if app:
            app._show_dashboard()

    def _find_app(self):
        """Walk up widget tree to find ProjsApp."""
        w = self.master
        while w is not None:
            if isinstance(w, ProjsApp):
                return w
            w = getattr(w, "master", None)
        return None

    def reset(self):
        if hasattr(self, "_wizard"):
            self._wizard.reset()


class SettingsPanel(_BasePanel):
    """Thin wrapper — delegates to the real panel in panels/settings.py."""

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._panel = _SettingsPanel(
            self,
            theme=self.theme,
            config=self.config,
            manifest_store=self.manifest_store,
            shortcuts=self.shortcuts,
        )
        self._panel.grid(row=0, column=0, sticky=NSEW)

    def refresh(self):
        if hasattr(self, "_panel"):
            self._panel.refresh()


class HelpPanel(_BasePanel):
    """Help and documentation panel."""

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        ttk.Label(
            self,
            text="Help",
            font=(self.theme.font_family, 16),
        ).pack(pady=20)
        ttk.Label(
            self,
            text="README and documentation will live here.",
            bootstyle=SECONDARY,
        ).pack()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Entry point for projs-gui command."""
    try:
        import tkinter  # pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        import platform  # pylint: disable=import-outside-toplevel
        import sys       # pylint: disable=import-outside-toplevel
        system = platform.system()
        print("Error: tkinter is not installed.")
        if system == "Linux":
            print("Install it with: sudo apt install python3-tk")
            print("                 sudo dnf install python3-tkinter  (Fedora/RHEL)")
            print("                 sudo pacman -S tk                 (Arch)")
        elif system == "Darwin":
            print("Install it with: brew install python-tk")
            print("Or reinstall Python from https://python.org (includes tkinter).")
        elif system == "Windows":
            print("Reinstall Python from https://python.org")
            print("Ensure 'tcl/tk and IDLE' is checked during installation.")
        else:
            print("See: https://tkdocs.com/tutorial/install.html")
        sys.exit(1)

    config = ConfigManager()
    theme = ThemeManager(config)

    app = ttk.Window(
        title="projs",
        themename=theme.ttkbootstrap_theme,
        size=(900, 600),
        resizable=(True, True),
    )

    ProjsApp(app, theme, config)
    app.mainloop()


if __name__ == "__main__":
    main()

```
