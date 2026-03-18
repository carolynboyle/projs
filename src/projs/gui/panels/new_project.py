"""
projs.gui.panels.new_project - Two-step new project wizard.

Step 1  Basics    — name, description, path, language, license
Step 2  Setup     — gitignore shuttle  |  commands shuttle
                    README checkbox, Create button

Shuttle widget layout (used for both gitignore and commands):
    [ Available listbox ]  >   [ Selected listbox ]
                           >>
                           <    Up / Down on Selected side
                           <<

Double-click shuttles an item in either direction.
Custom entry + Add button below the Available listbox (commands only).
"""

from pathlib import Path
from typing import List, Callable, Optional

import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # pylint: disable=wildcard-import,unused-wildcard-import

from projs.config import ConfigManager
from projs.manifest import ManifestStore, ProjectManifest, ManifestCommand
from projs.commands import CommandLibrary
from projs.gui.theme import ThemeManager
from projs.gui.shortcuts import ShortcutManager

_PANEL_ID = "new_project"


# ---------------------------------------------------------------------------
# Shuttle widget — reusable dual-listbox
# ---------------------------------------------------------------------------

class ShuttleWidget(ttk.Frame):
    """Dual-listbox shuttle: Available ←→ Selected.

    Args:
        master:         parent widget
        available:      initial items for the Available listbox  [(label, value), ...]
        with_reorder:   show Up/Down buttons on the Selected side
        with_custom:    show a custom-entry row below Available
        custom_prompt:  placeholder text for the custom entry
    """

    def __init__(
        self,
        master,
        available: List[tuple],
        with_reorder: bool = False,
        with_custom: bool = False,
        custom_prompt: str = "Custom entry…",
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._with_reorder = with_reorder
        self._with_custom = with_custom

        # Internal state: list of (label, value) tuples
        self._available: List[tuple] = list(available)
        self._selected: List[tuple] = []

        self._build(custom_prompt)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self, custom_prompt: str):
        self.columnconfigure(0, weight=1)  # Available
        self.columnconfigure(1, weight=0)  # Buttons
        self.columnconfigure(2, weight=1)  # Selected
        if self._with_reorder:
            self.columnconfigure(3, weight=0)  # Up/Down

        # --- Available listbox ---
        avail_frame = ttk.Frame(self)
        avail_frame.grid(row=0, column=0, sticky=NSEW, padx=(0, 4))
        avail_frame.columnconfigure(0, weight=1)
        avail_frame.rowconfigure(1, weight=1)

        ttk.Label(avail_frame, text="Available", bootstyle=SECONDARY).grid(
            row=0, column=0, sticky=W, pady=(0, 2)
        )

        self._avail_lb = ttk.Treeview(
            avail_frame, show="tree", selectmode=EXTENDED, height=8
        )
        self._avail_lb.grid(row=1, column=0, sticky=NSEW)
        avail_scroll = ttk.Scrollbar(avail_frame, orient=VERTICAL,
                                     command=self._avail_lb.yview)
        avail_scroll.grid(row=1, column=1, sticky=NS)
        self._avail_lb.configure(yscrollcommand=avail_scroll.set)
        self._avail_lb.bind("<Double-1>", lambda e: self._move_right())

        # Custom entry row (commands only)
        if self._with_custom:
            avail_frame.rowconfigure(2, weight=0)
            avail_frame.rowconfigure(3, weight=0)
            entry_frame = ttk.Frame(avail_frame)
            entry_frame.grid(row=2, column=0, columnspan=2, sticky=EW, pady=(6, 0))
            entry_frame.columnconfigure(0, weight=1)

            self._custom_var = ttk.StringVar()
            ttk.Entry(
                entry_frame,
                textvariable=self._custom_var,
            ).grid(row=0, column=0, sticky=EW)
            ttk.Button(
                entry_frame, text="Add", bootstyle=(SECONDARY, OUTLINE),
                width=5, command=self._add_custom,
            ).grid(row=0, column=1, padx=(4, 0))
            ttk.Label(
                avail_frame,
                text="Custom command",
                font=("", 8),
                bootstyle=SECONDARY,
                anchor=CENTER,
            ).grid(row=3, column=0, columnspan=2, sticky=EW, pady=(2, 0))

        # --- Shuttle buttons ---
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=0, column=1, padx=6)

        for text, cmd in [
            (">",  self._move_right),
            (">>", self._move_all_right),
            ("<",  self._move_left),
            ("<<", self._move_all_left),
        ]:
            ttk.Button(
                btn_frame, text=text, width=3,
                bootstyle=(SECONDARY, OUTLINE),
                command=cmd,
            ).pack(pady=2)

        # --- Selected listbox ---
        sel_frame = ttk.Frame(self)
        sel_frame.grid(row=0, column=2, sticky=NSEW, padx=(4, 0))
        sel_frame.columnconfigure(0, weight=1)
        sel_frame.rowconfigure(1, weight=1)

        ttk.Label(sel_frame, text="Selected", bootstyle=SECONDARY).grid(
            row=0, column=0, sticky=W, pady=(0, 2)
        )

        self._sel_lb = ttk.Treeview(
            sel_frame, show="tree", selectmode=EXTENDED, height=8
        )
        self._sel_lb.grid(row=1, column=0, sticky=NSEW)
        sel_scroll = ttk.Scrollbar(sel_frame, orient=VERTICAL,
                                   command=self._sel_lb.yview)
        sel_scroll.grid(row=1, column=1, sticky=NS)
        self._sel_lb.configure(yscrollcommand=sel_scroll.set)
        self._sel_lb.bind("<Double-1>", lambda e: self._move_left())

        # --- Up/Down buttons (commands only) ---
        if self._with_reorder:
            ud_frame = ttk.Frame(self)
            ud_frame.grid(row=0, column=3, padx=(4, 0))
            ttk.Button(
                ud_frame, text="▲", width=3,
                bootstyle=(SECONDARY, OUTLINE),
                command=self._move_up,
            ).pack(pady=2)
            ttk.Button(
                ud_frame, text="▼", width=3,
                bootstyle=(SECONDARY, OUTLINE),
                command=self._move_down,
            ).pack(pady=2)

        self._refresh_avail()
        self._refresh_sel()

    # ------------------------------------------------------------------
    # Listbox refresh helpers
    # ------------------------------------------------------------------

    def _refresh_avail(self):
        self._avail_lb.delete(*self._avail_lb.get_children())
        for label, _ in self._available:
            self._avail_lb.insert("", END, text=label)

    def _refresh_sel(self):
        self._sel_lb.delete(*self._sel_lb.get_children())
        for label, _ in self._selected:
            self._sel_lb.insert("", END, text=label)

    # ------------------------------------------------------------------
    # Shuttle operations
    # ------------------------------------------------------------------

    def _selected_avail_indices(self) -> List[int]:
        items = self._avail_lb.selection()
        all_items = self._avail_lb.get_children()
        return [all_items.index(i) for i in items if i in all_items]

    def _selected_sel_indices(self) -> List[int]:
        items = self._sel_lb.selection()
        all_items = self._sel_lb.get_children()
        return [all_items.index(i) for i in items if i in all_items]

    def _move_right(self):
        indices = self._selected_avail_indices()
        if not indices:
            return
        moving = [self._available[i] for i in sorted(indices, reverse=True)]
        for i in sorted(indices, reverse=True):
            self._available.pop(i)
        self._selected.extend(reversed(moving))
        self._refresh_avail()
        self._refresh_sel()

    def _move_all_right(self):
        self._selected.extend(self._available)
        self._available.clear()
        self._refresh_avail()
        self._refresh_sel()

    def _move_left(self):
        indices = self._selected_sel_indices()
        if not indices:
            return
        moving = [self._selected[i] for i in sorted(indices, reverse=True)]
        for i in sorted(indices, reverse=True):
            self._selected.pop(i)
        self._available.extend(reversed(moving))
        self._refresh_avail()
        self._refresh_sel()

    def _move_all_left(self):
        self._available.extend(self._selected)
        self._selected.clear()
        self._refresh_avail()
        self._refresh_sel()

    def _move_up(self):
        indices = self._selected_sel_indices()
        if not indices or indices[0] == 0:
            return
        for i in indices:
            self._selected[i - 1], self._selected[i] = (
                self._selected[i], self._selected[i - 1]
            )
        self._refresh_sel()

    def _move_down(self):
        indices = self._selected_sel_indices()
        if not indices or indices[-1] == len(self._selected) - 1:
            return
        for i in reversed(indices):
            self._selected[i], self._selected[i + 1] = (
                self._selected[i + 1], self._selected[i]
            )
        self._refresh_sel()

    def _add_custom(self):
        val = self._custom_var.get().strip()
        if not val:
            return
        self._selected.append((val, f"custom: {val}"))
        self._custom_var.set("")
        self._refresh_sel()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_selected_values(self) -> List[str]:
        """Return the value component of each selected item, in order."""
        return [v for _, v in self._selected]

    def set_available(self, items: List[tuple]):
        """Replace the Available list (resets Selected too)."""
        self._available = list(items)
        self._selected = []
        self._refresh_avail()
        self._refresh_sel()


# ---------------------------------------------------------------------------
# Step indicator strip
# ---------------------------------------------------------------------------

class _StepIndicator(ttk.Frame):
    """Horizontal step indicator — highlights the active step label."""

    def __init__(self, master, steps: List[str], **kwargs):
        super().__init__(master, **kwargs)
        self._labels = []
        for i, name in enumerate(steps):
            lbl = ttk.Label(self, text=f"{'→ ' if i else ''}{name}",
                            font=("", 10))
            lbl.pack(side=LEFT, padx=(0, 16))
            self._labels.append(lbl)
        self.set_step(0)

    def set_step(self, index: int):
        for i, lbl in enumerate(self._labels):
            lbl.configure(bootstyle=PRIMARY if i == index else SECONDARY)


# ---------------------------------------------------------------------------
# NewProjectPanel
# ---------------------------------------------------------------------------

class NewProjectPanel(ttk.Frame):
    """Two-step new project creation wizard.

    Designed to be used as a stacked panel inside ProjsApp._main.
    The parent must pass on_done(manifest) and on_cancel() callbacks.
    """

    def __init__(
        self,
        master,
        theme: ThemeManager,
        config: ConfigManager,
        manifest_store: ManifestStore,
        shortcuts: ShortcutManager,
        on_done: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.config = config
        self.manifest_store = manifest_store
        self.shortcuts = shortcuts
        self.on_done = on_done
        self.on_cancel = on_cancel

        self._command_library = CommandLibrary(config)

        # Step tracking
        self._step = 0

        # Editor vars (step 2)
        self._editor_var = ttk.StringVar()
        self._custom_editor_var = ttk.StringVar()

        # Step 1 vars
        self._name_var = ttk.StringVar()
        self._desc_var = ttk.StringVar()
        self._path_var = ttk.StringVar()
        self._lang_var = ttk.StringVar()
        self._license_var = ttk.StringVar()
        self._readme_var = ttk.BooleanVar(value=True)

        # Error label var
        self._error_var = ttk.StringVar()

        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)  # content area expands

        # Step indicator
        self._step_indicator = _StepIndicator(
            self, steps=["1  Basics", "2  Setup"]
        )
        self._step_indicator.grid(row=0, column=0, sticky=EW, padx=20, pady=(12, 0))

        # Content area — stacked frames, one per step
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky=NSEW, padx=20, pady=10)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        self._step1 = self._build_step1(content)
        self._step1.grid(row=0, column=0, sticky=NSEW)

        self._step2 = self._build_step2(content)
        self._step2.grid(row=0, column=0, sticky=NSEW)

        # Error strip
        ttk.Label(
            self,
            textvariable=self._error_var,
            bootstyle=DANGER,
            font=("", 9),
        ).grid(row=2, column=0, sticky=W, padx=20)

        # Nav buttons
        nav = ttk.Frame(self, padding=(20, 6))
        nav.grid(row=3, column=0, sticky=EW)

        self._cancel_btn = ttk.Button(
            nav, text="Cancel", bootstyle=(SECONDARY, OUTLINE),
            command=self._do_cancel,
        )
        self._cancel_btn.pack(side=LEFT)

        self._back_btn = ttk.Button(
            nav, text="← Back", bootstyle=(SECONDARY, OUTLINE),
            command=self._do_back, state=DISABLED,
        )
        self._back_btn.pack(side=LEFT, padx=(8, 0))

        self._next_btn = ttk.Button(
            nav, text="Next →", bootstyle=PRIMARY,
            command=self._do_next,
        )
        self._next_btn.pack(side=RIGHT)

        editors = self.config.get_editors()
        if editors:
            self._editor_var.set(editors[0])
        self._custom_editor_var.set("")
        self._show_step(0)

    def _build_step1(self, master) -> ttk.Frame:
        """Step 1 — Basics: name, description, path, language, license."""
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        row = 0
        fields = [
            ("Name",        self._name_var,    False),
            ("Description", self._desc_var,    False),
            ("Path",        self._path_var,    False),
        ]
        for label, var, _ in fields:
            ttk.Label(frame, text=label).grid(
                row=row, column=0, sticky=W, pady=4, padx=(0, 12)
            )
            entry = ttk.Entry(frame, textvariable=var)
            entry.grid(row=row, column=1, sticky=EW, pady=4)
            row += 1

        # Auto-fill path when name changes
        self._name_var.trace_add("write", self._on_name_change)

        # Language
        ttk.Label(frame, text="Language").grid(
            row=row, column=0, sticky=W, pady=4, padx=(0, 12)
        )
        languages = self.config.get_languages()
        lang_cb = ttk.Combobox(
            frame, textvariable=self._lang_var,
            values=languages, state="readonly",
        )
        if languages:
            lang_cb.current(0)
        lang_cb.grid(row=row, column=1, sticky=EW, pady=4)
        row += 1

        # License
        ttk.Label(frame, text="License").grid(
            row=row, column=0, sticky=W, pady=4, padx=(0, 12)
        )
        licenses = self.config.get_licenses()
        lic_cb = ttk.Combobox(
            frame, textvariable=self._license_var,
            values=licenses, state="readonly",
        )
        if licenses:
            lic_cb.current(0)
        lic_cb.grid(row=row, column=1, sticky=EW, pady=4)

        return frame

    def _build_step2(self, master) -> ttk.Frame:
        """Step 2 — Setup: gitignore shuttle + commands shuttle + README.

        Wrapped in a Canvas so the custom entry rows are always reachable
        regardless of window height.
        """
        # Outer container holds canvas + scrollbar
        outer = ttk.Frame(master)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        canvas = ttk.Canvas(outer, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky=NSEW)
        vsb = ttk.Scrollbar(outer, orient=VERTICAL, command=canvas.yview)
        vsb.grid(row=0, column=1, sticky=NS)
        canvas.configure(yscrollcommand=vsb.set)

        # Inner frame — actual content lives here
        frame = ttk.Frame(canvas)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)
        canvas_win = canvas.create_window((0, 0), window=frame, anchor=NW)

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_win, width=e.width)

        frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse wheel — Linux Button-4/5 and Windows/Mac delta
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Gitignore section
        ttk.Label(frame, text=".gitignore entries",
                  font=("", 10, "bold")).grid(
            row=0, column=0, sticky=W, pady=(0, 4)
        )
        self._gitignore_shuttle = ShuttleWidget(
            frame,
            available=[],
            with_reorder=False,
            with_custom=True,
            custom_prompt="custom entry…",
        )
        self._gitignore_shuttle.grid(row=1, column=0, sticky=NSEW, padx=(0, 12))

        # Commands section
        cmd_header = ttk.Frame(frame)
        cmd_header.grid(row=0, column=1, sticky=EW, pady=(0, 4))
        cmd_header.columnconfigure(1, weight=1)

        ttk.Label(cmd_header, text="Launch commands",
                  font=("", 10, "bold")).grid(row=0, column=0, sticky=W)

        # Editor selector — inline with commands header
        ttk.Label(cmd_header, text="Editor:",
                  font=("", 9)).grid(row=0, column=2, sticky=E, padx=(12, 4))
        editors = self.config.get_editors()
        self._editor_cb = ttk.Combobox(
            cmd_header,
            textvariable=self._editor_var,
            values=editors,
            state="readonly",
            width=12,
        )
        self._editor_cb.grid(row=0, column=3, sticky=E)
        self._editor_var.trace_add("write", self._on_editor_change)

        # Custom editor entry — shown when "custom" selected
        self._custom_editor_entry = ttk.Entry(
            cmd_header,
            textvariable=self._custom_editor_var,
            width=14,
        )
        self._custom_editor_entry.grid(row=0, column=4, sticky=E, padx=(4, 0))
        self._custom_editor_entry.grid_remove()

        self._commands_shuttle = ShuttleWidget(
            frame,
            available=[],
            with_reorder=True,
            with_custom=True,
            custom_prompt="shell command…",
        )
        self._commands_shuttle.grid(row=1, column=1, sticky=NSEW)

        # README checkbox
        ttk.Checkbutton(
            frame,
            text="Create README.md",
            variable=self._readme_var,
            bootstyle="round-toggle",
        ).grid(row=2, column=0, sticky=W, pady=(10, 0))

        return outer

    # ------------------------------------------------------------------
    # Step navigation
    # ------------------------------------------------------------------

    def _show_step(self, step: int):
        self._step = step
        self._step_indicator.set_step(step)
        self._error_var.set("")

        if step == 0:
            self._step1.tkraise()
            self._back_btn.configure(state=DISABLED)
            self._next_btn.configure(text="Next →", bootstyle=PRIMARY)
        else:
            self._step2.tkraise()
            self._populate_step2()
            self._back_btn.configure(state=NORMAL)
            self._next_btn.configure(text="Create", bootstyle=SUCCESS)

    def _populate_step2(self):
        """Fill both shuttles based on current language selection."""
        language = self._lang_var.get()

        # Gitignore — defaults for selected language
        gi_entries = self.config.get_gitignore(language)
        self._gitignore_shuttle.set_available(
            [(e, e) for e in gi_entries]
        )

        # Commands — full library
        all_cmds = self._command_library.get_all()
        self._commands_shuttle.set_available(
            [(cmd["name"], cmd["id"]) for cmd in all_cmds]
        )

        # Editor — pre-select configured default
        editors = self.config.get_editors()
        current = self.config.get_editor()
        if current in editors:
            self._editor_var.set(current)
        elif current:
            self._editor_var.set("custom")
            self._custom_editor_var.set(current)
        elif editors:
            self._editor_var.set(editors[0])

    def _do_next(self):
        if self._step == 0:
            if self._validate_step1():
                self._show_step(1)
        else:
            self._do_create()

    def _do_back(self):
        if self._step == 1:
            self._show_step(0)

    def _do_cancel(self):
        if self.on_cancel:
            self.on_cancel()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_step1(self) -> bool:
        name = self._name_var.get().strip()
        if not name:
            self._error_var.set("Project name is required.")
            return False
        if self.manifest_store.load(name):
            self._error_var.set(f"A project named '{name}' already exists.")
            return False
        if not self._lang_var.get():
            self._error_var.set("Please select a language.")
            return False
        if not self._license_var.get():
            self._error_var.set("Please select a license.")
            return False
        self._error_var.set("")
        return True

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def _do_create(self):
        name        = self._name_var.get().strip()
        description = self._desc_var.get().strip()
        language    = self._lang_var.get()
        proj_license = self._license_var.get()
        path        = self._path_var.get().strip() or f"~/projects/{name}"

        # Build gitignore list
        gitignore = self._gitignore_shuttle.get_selected_values()

        # Determine editor for this project
        editor = self._editor_var.get()
        if editor == "custom":
            editor = self._custom_editor_var.get().strip()

        # Build ManifestCommand list from shuttle order
        cmd_values = self._commands_shuttle.get_selected_values()
        commands: List[ManifestCommand] = []
        seq = 10
        for val in cmd_values:
            if val.startswith("custom: "):
                cmd_str = val[8:]
                commands.append(ManifestCommand(
                    seq=seq, command=cmd_str, description=cmd_str
                ))
            else:
                # Library ID — look up name for description
                cmd_obj = self._command_library.get_by_id(val)
                desc = cmd_obj["name"] if cmd_obj else val
                commands.append(ManifestCommand(
                    seq=seq, command=val, description=desc
                ))
            seq += 10

        # Editor goes last at seq 90 (convention: always the final launch step)
        if editor and editor != "custom":
            commands.append(ManifestCommand(
                seq=90,
                command=f"{editor} .",
                description=f"Launch {editor}",
            ))

        manifest = ProjectManifest(
            name=name,
            description=description,
            language=language,
            path=path,
            proj_license=proj_license,
            gitignore=gitignore,
            commands=commands,
        )

        # Create project directory
        try:
            project_path = manifest.expanded_path()
            project_path.mkdir(parents=True, exist_ok=True)

            if self._readme_var.get():
                readme = project_path / "README.md"
                readme.write_text(f"# {name}\n\n{description}\n")

            self.manifest_store.save(manifest)
        except Exception as exc:
            self._error_var.set(f"Error creating project: {exc}")
            return

        if self.on_done:
            self.on_done(manifest)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _on_editor_change(self, *_):
        """Show/hide custom editor entry."""
        if self._editor_var.get() == "custom":
            self._custom_editor_entry.grid()
        else:
            self._custom_editor_entry.grid_remove()

    def _on_name_change(self, *_):
        name = self._name_var.get().strip()
        self._path_var.set(f"~/projects/{name}" if name else "")

    def reset(self):
        """Clear all fields and return to step 1."""
        self._name_var.set("")
        self._desc_var.set("")
        self._path_var.set("")
        self._readme_var.set(True)
        self._error_var.set("")
        languages = self.config.get_languages()
        if languages:
            self._lang_var.set(languages[0])
        licenses = self.config.get_licenses()
        if licenses:
            self._license_var.set(licenses[0])
        self._show_step(0)
