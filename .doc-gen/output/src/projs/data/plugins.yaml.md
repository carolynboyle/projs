# plugins.yaml

**Path:** src/projs/data/plugins.yaml
**Syntax:** yaml
**Generated:** 2026-03-22 18:36:59

```yaml
# projs plugin configuration
# User copy: ~/.projects/config/plugins.yaml
# Shipped default: projs/data/plugins.yaml
#
# Export destinations are additive — docs/TODO.md is always written.
# Add entries under 'export' to also send to external destinations.
#
# Supported export types:
#   folder:   copy TODO.md to an arbitrary local path
#   obsidian: write to an Obsidian vault via file path
#             (use obsidian:// URIs in todo links for deep linking)

todo:
  output_dir: docs
  filename: TODO.md

  # export:
  #   - type: folder
  #     path: ~/Dropbox/todos
  #
  #   - type: obsidian
  #     vault_path: ~/Documents/ObsidianVault
  #     folder: projects

```
