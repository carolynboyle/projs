# architecture.md

**Path:** docs/architecture.md
**Syntax:** markdown
**Generated:** 2026-03-25 09:30:03

```markdown
projs/
├── README.md
├── pyproject.toml              # Package config + entry points
├── .gitignore
│
├── src/
│   └── projs/
│       ├── __init__.py
│       ├── main.py             # CLI entry point & menu loop
│       ├── config.py           # ConfigManager
│       ├── manifest.py         # ProjectManifest, ManifestStore
│       ├── prompts.py          # PromptHelper
│       ├── commands.py         # CommandLibrary
│       ├── language_actions.py # LanguageActions
│       ├── tmux.py             # TMuxSession
│       ├── creator.py          # Project creation flow
│       ├── launcher.py         # Project launch flow
│       └── modifier.py         # Project modification flow
│
├── templates/
│   ├── python-basic.yaml       # Project structure templates (phase 2)
│   └── flutter-game.yaml
│
├── licenses/                   # (phase 2: license text files)
│   ├── MIT.txt
│   ├── GPL-v3.txt
│   └── Apache-2.0.txt
│
├── systemd/                    # (phase 3: background task runner)
│   └── projs-worker.service
│
└── tests/
    ├── test_manifest.py
    ├── test_commands.py
    └── ...
```
