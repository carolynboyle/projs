# dashboard.py

**Path:** src/projs/gui/panels/dashboard.py
**Syntax:** python
**Generated:** 2026-03-22 18:36:59

```python
"""
projs.gui.panels.dashboard - Project list and detail view.

Layout
------
  Left pane  (Notebook)
    Tab 0  Projects  — scrollable project list
    Tab 1  Commands  — launch sequence for selected project
    Tab 2  Todo      — project todo list (plugin stub)

  Right pane
    Info strip  — name, language, license, path, description,
                  last launched (placeholder until logger exists)

  Action buttons live in the app header, not here.
  This panel calls on_select(manifest) so the header can update.
"""

import threading

import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # pylint: disable=wildcard-import,unused-wildcard-import

from projs.config import ConfigManager
from projs.manifest import ManifestStore, ProjectManifest
from projs.cli.launcher import ProjectLauncher
from projs.cli.prompts import PromptHelper
from projs.gui.theme import ThemeManager
from projs.gui.shortcuts import ShortcutManager

_PANEL_ID = "dashboard"


class DashboardPanel(ttk.Frame):
    """Project list and detail view panel."""

    def __init__(self, master, theme: ThemeManager, config: ConfigManager,
                 manifest_store: ManifestStore, shortcuts: ShortcutManager,
                 on_select=None, on_create=None, on_import=None, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.config = config
        self.manifest_store = manifest_store
        self.shortcuts = shortcuts
        self.on_select = on_select   # callback(manifest | None) → updates header
        self.on_create = on_create   # callback() → switch to NewProjectPanel
        self.on_import = on_import   # callback() → switch to ImportPanel (future)

        self._selected: ProjectManifest | None = None

        # Widget refs — assigned in _build*
        self._notebook: ttk.Notebook | None = None
        self._listbox: ttk.Treeview | None = None
        self._cmd_list: ttk.Treeview | None = None
        self._fields: dict = {}
        self._empty_state: ttk.Frame | None = None
        self._detail_view: ttk.Frame | None = None
        self._cmd_empty_label: ttk.Label | None = None
        self._todo_empty_label: ttk.Label | None = None

        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self):
        """Two-column responsive layout."""
        self.columnconfigure(0, weight=1)   # left pane (notebook) — expands
        self.columnconfigure(1, weight=2)   # right pane (detail)  — expands more
        self.rowconfigure(0, weight=1)

        self._build_left_pane()
        self._build_right_pane()

    def _build_left_pane(self):
        """Notebook with Projects / Commands / Todo tabs."""
        self._notebook = ttk.Notebook(self)
        self._notebook.grid(row=0, column=0, sticky=NSEW, padx=(8, 4), pady=8)

        self._build_projects_tab()
        self._build_commands_tab()
        self._build_todo_tab()

        # Register tab shortcuts
        self.shortcuts.register(
            self._notebook, panel_id=_PANEL_ID,
            key="p", underline=0,
            callback=lambda: self._notebook.select(0),
        )
        self.shortcuts.register(
            self._notebook, panel_id=_PANEL_ID,
            key="m", underline=2,
            callback=lambda: self._notebook.select(1),
        )
        self.shortcuts.register(
            self._notebook, panel_id=_PANEL_ID,
            key="t", underline=0,
            callback=lambda: self._notebook.select(2),
        )

    def _build_projects_tab(self):
        """Tab 0 — scrollable project list."""
        frame = ttk.Frame(self._notebook)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self._notebook.add(frame, text="Projects")

        list_frame = ttk.Frame(frame)
        list_frame.grid(row=0, column=0, sticky=NSEW, padx=4, pady=4)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=NS)

        self._listbox = ttk.Treeview(
            list_frame,
            columns=("language",),
            show="tree headings",
            selectmode=BROWSE,
            yscrollcommand=scrollbar.set,
        )
        self._listbox.heading("#0", text="Name")
        self._listbox.heading("language", text="Lang")
        self._listbox.column("#0", width=140, stretch=YES)
        self._listbox.column("language", width=60, anchor=CENTER, stretch=NO)
        self._listbox.grid(row=0, column=0, sticky=NSEW)
        scrollbar.configure(command=self._listbox.yview)

        self._listbox.bind("<<TreeviewSelect>>", self._on_select)

    def _build_commands_tab(self):
        """Tab 1 — launch sequence for the selected project."""
        frame = ttk.Frame(self._notebook)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self._notebook.add(frame, text="Commands")

        # Empty state — shown until a project is selected
        self._cmd_empty_label = ttk.Label(
            frame,
            text="Select a project to view its launch sequence.",
            bootstyle=SECONDARY,
        )
        self._cmd_empty_label.grid(row=0, column=0, pady=40)

        # Command treeview — hidden until a project is selected
        cmd_frame = ttk.Frame(frame)
        cmd_frame.columnconfigure(0, weight=1)
        cmd_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(cmd_frame)
        scrollbar.grid(row=0, column=1, sticky=NS)

        self._cmd_list = ttk.Treeview(
            cmd_frame,
            columns=("seq", "command", "description"),
            show="headings",
            selectmode=NONE,
            yscrollcommand=scrollbar.set,
        )
        self._cmd_list.heading("seq",         text="Seq")
        self._cmd_list.heading("command",     text="Command")
        self._cmd_list.heading("description", text="Description")
        self._cmd_list.column("seq",         width=40,  anchor=CENTER, stretch=NO)
        self._cmd_list.column("command",     width=180, stretch=YES)
        self._cmd_list.column("description", width=160, stretch=YES)
        self._cmd_list.grid(row=0, column=0, sticky=NSEW)
        scrollbar.configure(command=self._cmd_list.yview)

        # Store cmd_frame ref so we can show/hide it
        self._cmd_frame = cmd_frame

    def _build_todo_tab(self):
        """Tab 2 — project todo list (plugin stub)."""
        frame = ttk.Frame(self._notebook)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self._notebook.add(frame, text="Todo")

        self._todo_empty_label = ttk.Label(
            frame,
            text="Todo plugin coming soon.\nSelect a project to view its tasks.",
            bootstyle=SECONDARY,
            justify=CENTER,
        )
        self._todo_empty_label.grid(row=0, column=0, pady=40)

    def _build_right_pane(self):
        """Info strip + first-run empty state."""
        self._detail = ttk.Frame(self, padding=10)
        self._detail.grid(row=0, column=1, sticky=NSEW, padx=(4, 8), pady=8)
        self._detail.columnconfigure(0, weight=1)
        self._detail.rowconfigure(1, weight=1)

        # --- Empty state (no projects at all) ---
        self._empty_state = ttk.Frame(self._detail)
        self._empty_state.grid(row=0, column=0, sticky=NSEW, pady=60)
        self._empty_state.columnconfigure(0, weight=1)

        ttk.Label(
            self._empty_state,
            text="No projects yet.",
            font=(self.theme.font_family, 13),
            bootstyle=SECONDARY,
        ).pack(pady=(0, 16))

        btn_frame = ttk.Frame(self._empty_state)
        btn_frame.pack()

        ttk.Button(
            btn_frame,
            text="Create first project",
            bootstyle=INFO,
            command=self._do_create,
        ).pack(side=LEFT, padx=6)

        ttk.Button(
            btn_frame,
            text="Import existing project",
            bootstyle=SECONDARY,
            command=self._do_import,
        ).pack(side=LEFT, padx=6)

        # --- Detail view (shown when a project is selected) ---
        self._detail_view = ttk.Frame(self._detail)
        self._detail_view.grid(row=0, column=0, sticky=NSEW)
        self._detail_view.columnconfigure(1, weight=1)

        info = ttk.Labelframe(self._detail_view, text="Project", padding=10)
        info.grid(row=0, column=0, columnspan=2, sticky=EW, pady=(0, 8))
        info.columnconfigure(1, weight=1)

        self._fields = {}
        field_defs = [
            ("Name",          "name"),
            ("Language",      "language"),
            ("License",       "license"),
            ("Path",          "path"),
            ("Description",   "description"),
            ("Last launched", "last_launched"),
        ]
        for i, (label, key) in enumerate(field_defs):
            ttk.Label(
                info,
                text=f"{label}:",
                font=(self.theme.font_family, 10, "bold"),
            ).grid(row=i, column=0, sticky=W, padx=(0, 10), pady=2)
            var = ttk.StringVar()
            ttk.Label(
                info,
                textvariable=var,
                wraplength=320,
            ).grid(row=i, column=1, sticky=W, pady=2)
            self._fields[key] = var

        # Start hidden — shown once a project exists
        self._detail_view.grid_remove()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def refresh(self):
        """Reload project list from manifest store."""
        self._listbox.delete(*self._listbox.get_children())
        manifests = self.manifest_store.list_all()

        if not manifests:
            self._detail_view.grid_remove()
            self._empty_state.grid()
            self._notify_selection(None)
            return

        self._empty_state.grid_remove()

        for m in manifests:
            self._listbox.insert(
                "", END, iid=m.name, text=m.name, values=(m.language,)
            )

        # Auto-select first project
        first = self._listbox.get_children()[0]
        self._listbox.selection_set(first)
        self._listbox.focus(first)

    def select_project(self, name: str):
        """Select a project by name in the listbox (called after creation)."""
        children = self._listbox.get_children()
        if name in children:
            self._listbox.selection_set(name)
            self._listbox.focus(name)
            self._listbox.see(name)
            # Trigger the selection callback manually
            self._on_select(None)

    def do_launch(self):
        """Called by app header Launch button — runs launcher on a background thread.

        gui_mode=True means the launcher sets up the tmux session and sends all
        commands, but skips the blocking attach() call so the GUI stays live.
        The user switches to their terminal and runs:
            tmux attach-session -t <project_name>
        """
        if not self._selected:
            return
        prompt = PromptHelper()
        launcher = ProjectLauncher(self.config, self._selected, prompt)
        t = threading.Thread(
            target=launcher.run,
            kwargs={"gui_mode": True},
            daemon=True,
        )
        t.start()

    def do_modify(self):
        """Called by app header Modify button."""
        # TODO: wire to ModifyPanel

    def do_delete(self):
        """Called by app header Delete button."""
        if not self._selected:
            return

        confirm1 = ttk.dialogs.Messagebox.yesno(
            message=f"Delete project '{self._selected.name}'?\nThis cannot be undone.",
            title="Confirm Delete",
            alert=True,
        )
        if confirm1 != "Yes":
            return

        confirm2 = ttk.dialogs.Messagebox.yesno(
            message=f"Final confirmation: permanently delete '{self._selected.name}'?",
            title="Are you sure?",
            alert=True,
        )
        if confirm2 != "Yes":
            return

        self.manifest_store.delete(self._selected.name)
        self._selected = None
        self._notify_selection(None)
        self.refresh()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_select(self, _event):
        """Populate detail panel when a project row is selected."""
        sel = self._listbox.selection()
        if not sel:
            return

        manifest = self.manifest_store.load(sel[0])
        if not manifest:
            return

        self._selected = manifest

        # Info strip
        self._fields["name"].set(manifest.name)
        self._fields["language"].set(manifest.language)
        self._fields["license"].set(manifest.license)
        self._fields["path"].set(manifest.path)
        self._fields["description"].set(manifest.description or "—")
        self._fields["last_launched"].set("—")  # placeholder until logger exists

        # Commands tab
        self._populate_commands(manifest)

        self._detail_view.grid()
        self._empty_state.grid_remove()
        self._notify_selection(manifest)

    def _populate_commands(self, manifest: ProjectManifest):
        """Fill the Commands tab treeview for *manifest*."""
        self._cmd_list.delete(*self._cmd_list.get_children())

        self._cmd_list.insert("", END, values=(
            "0", f"cd {manifest.expanded_path()}", "automatic",
        ), tags=("auto",))
        self._cmd_list.tag_configure("auto", foreground="gray")

        for cmd in manifest.sorted_commands():
            self._cmd_list.insert("", END, values=(
                cmd.seq, cmd.command, cmd.description or "",
            ))

        # Swap empty label for treeview
        self._cmd_empty_label.grid_remove()
        self._cmd_frame.grid(row=0, column=0, sticky=NSEW,
                             padx=4, pady=4)

    def _notify_selection(self, manifest: ProjectManifest | None):
        """Propagate selection up to ProjsApp so header can update."""
        if self.on_select:
            self.on_select(manifest)

    def _do_create(self):
        if self.on_create:
            self.on_create()

    def _do_import(self):
        if self.on_import:
            self.on_import()

```
