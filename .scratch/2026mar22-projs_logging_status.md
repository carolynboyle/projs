# projs logging — Current Status & Next Steps

## What's Done

### Logging Design (Finalized)
- **3-level system:** DEBUG, INFO, ERROR (respects user settings in `system.yaml`)
- **Dual destinations:** 
  - User local: `~/.projects/logs/projs.log` + per-project logs in `~/.projects/logs/projects/<name>/`
  - Global: `/opt/venvs/tools/logs/projs.log` (or fallback to package location)
- **Per-project structure:** `debug.log`, `info.log`, `error.log` (one per level, chronological)
- **Daily rotation:** Log files auto-rename with date suffix when day changes
- **Graceful degradation:** Permission denied → log locally + warn to stderr

### Code (Parts 1, 2, 3 saved in `.../projs/.scratch`)

**Part 1: Foundation**
- `__init__()` — sets up log directories, reads config
- `_should_log()` — filters by level (debug 0, info 1, error 2)
- `_format_message()` — timestamp + level + text

**Part 2: Writing & Public API**
- `_write_to_file()` — appends to file, creates dirs
- `.debug()`, `.info()`, `.error()` — public methods
- Optional params: `project="name"`, `global_event=True`

**Part 3: Advanced**
- `_rotate_if_needed()` — daily log rotation
- `error_with_traceback()` — log exceptions with full stack

### Mermaid Flowchart (Complete)
Visual diagram of logging flow: entry → filter → format → route → write → rotate → success/error

### Project Crew
- **Dr. Filewalker** — documents code (🩺)
- **Fletcher** — generates GitHub URLs from manifests
- **The Surveyor** (backlog) — maps menu flows to Mermaid diagrams, generates plat maps
- **The Signalman** (earlier consideration, not chosen)

## What's Next

### Immediate (This Conversation)
1. **Assemble `logging.py`**
   - Combine Parts 1, 2, 3 from `.scratch`
   - Collect all imports at top (deduplicate)
   - Class definition with all methods in order
   - Save to `src/projs/logging.py`

2. **Integration into app**
   - Update `config.py`: add `.get_log_level()` accessor
   - Update shipped `system.yaml`: add logging config defaults
   - Update `_setup.py`: prompt for log level on first run
   - Wire logger into `creator.py`, `launcher.py`, `modifier.py`

3. **Manual testing**
   - Create a test project
   - Check that logs appear in the right places
   - Verify rotation works (manual date test if needed)

### Next Conversation
**Start with:** "Ready to test logging or move to pytest setup?"

Options after manual testing:
- **A) Test manually first** — run app, create project, inspect logs
- **B) Jump to integration** — wire into creator.py, then test
- **C) Get pytest set up** — write actual tests that verify logging works

**Then:** Start the promised pytest conversation
- Fetch existing test stubs from repo
- Build first test (likely ProjectDraft serialization)
- Integrate logging into test infrastructure

## Key Files to Touch

- `src/projs/logging.py` — NEW
- `src/projs/config.py` — add log level accessor
- `src/projs/data/system.yaml` — add logging section
- `src/projs/_setup.py` — prompt for log level
- `src/projs/cli/creator.py` — add logger calls
- `src/projs/cli/launcher.py` — add logger calls
- `src/projs/cli/modifier.py` — add logger calls

## Architecture Notes

- Logger reads `system.yaml` for level setting (user-controlled)
- Global logs go to installed package location (fallback to detect at runtime)
- App is multi-user: each user gets their own `~/.projects/logs/`
- Permission denied → graceful fallback (local log + stderr warning)
- Tests can use the same logging infrastructure (log to temp location)

## Backlog Items

- **The Surveyor plugin** — scans YAML menus, generates Mermaid flowcharts (`project_plat.mmd`)
- **Admin group permissions** — `/opt/projs/logs/` writable only by `projs` group
- **Log cleanup** — archive/delete old rotated logs after N days
- **Log viewer** — GUI panel to browse project logs, filter by level
