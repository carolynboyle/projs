# platforms.yaml

**Path:** src/projs/data/platforms.yaml
**Syntax:** yaml
**Generated:** 2026-03-22 18:36:59

```yaml
linux:
  default: apt
  detectors:
    - file: /etc/fedora-release
      manager: dnf
    - file: /etc/redhat-release
      manager: dnf
    - file: /etc/debian_version
      manager: apt
    - file: /etc/arch-release
      manager: pacman
    - file: /etc/gentoo-release
      manager: emerge
  options:
    - dnf
    - apt
    - pacman
    - pacaur
    - emerge
    - brew
    - zypper

darwin:
  default: brew
  options:
    - brew
    - port

windows:
  default: choco
  options:
    - choco
    - scoop
    - winget

other:
  default: unknown
  options: []

```
