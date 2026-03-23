# commands.json

**Path:** src/projs/data/commands.json
**Syntax:** json
**Generated:** 2026-03-22 18:36:59

```json
{
  "commands": [
    {
      "id": "venv",
      "name": "Create virtual environment",
      "command": "python3 -m venv .venv"
    },
    {
      "id": "activate",
      "name": "Activate venv",
      "command": "source .venv/bin/activate"
    },
    {
      "id": "git_init",
      "name": "Initialize git",
      "command": "git init"
    },
    {
      "id": "git_commit",
      "name": "Initial commit",
      "command": "git add . && git commit -m \"Initial project scaffold\"",
      "tags": ["create_only"]
    }
  ]
}

```
