# pyproject.toml

**Path:** pyproject.toml
**Syntax:** toml
**Generated:** 2026-03-25 09:30:03

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "projs"
version = "0.1.0"
description = "Project launcher and setup manager for homelab"
authors = [
    {name = "Carolyn Boyle", email = "carolyn@whyacantyoujust.tech"}
]
requires-python = ">=3.11"
dependencies = [
    "PyYAML>=6.0",
]

[project.scripts]
projs = "projs.cli.main:cli"
projs-gui = "projs.gui.app:main"

[project.optional-dependencies]
gui = [
    "ttkbootstrap>=1.10",
]
dev = [
    "pytest>=7.0",
    "black>=23.0",
    "mypy>=1.0",
    "pylint>=3.0",
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages]
find = {where = ["src"]}

[tool.pylint.format]
max-line-length = 120


[tool.setuptools.package-data]
projs = [
    "data/*.yaml",
    "data/*.json",
    "data/language-actions/*.yaml",
    "data/licenses/*.txt",         # ← add this
    "data/themes/**/*.yaml",
    "data/themes/**/*.png",
]
```
