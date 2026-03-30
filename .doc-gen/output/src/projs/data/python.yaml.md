# python.yaml

**Path:** src/projs/data/python.yaml
**Syntax:** yaml
**Generated:** 2026-03-25 09:30:03

```yaml
actions:
  - name: Create virtual environment
    type: shell
    command: python3 -m venv .venv

  - name: Activate virtual environment
    type: shell
    command: source .venv/bin/activate

  - name: Upgrade pip
    type: shell
    command: pip install --upgrade pip

```
