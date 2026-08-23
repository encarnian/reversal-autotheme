# Reversal Auto-Theme: Project Packaging & Cross-Distro Distribution

## Overview
We will create a structured, production-grade project repository for **Reversal Auto-Theme** in `/home/ausamnco/.gemini/antigravity/scratch/reversal-autotheme`. The project will be packaged for universal installation across Linux distributions (Arch Linux AUR, Debian/Ubuntu `.deb`, Fedora/RHEL `.rpm`, universal Makefile/`install.sh`, and PyPI/`pipx`).

---

## User Review Required

> [!NOTE]
> The project will be created inside `/home/ausamnco/.gemini/antigravity/scratch/reversal-autotheme`. We recommend setting this directory as your active workspace in Antigravity.

---

## Project Structure & Architecture

```text
reversal-autotheme/
├── pyproject.toml                     # Modern PEP 621 / setuptools configuration
├── setup.py                           # Standard Python setup script
├── Makefile                           # Universal build & install targets (system/user/deb/rpm/arch)
├── install.sh                         # One-line universal installer script for any distro
├── README.md                          # Comprehensive user & developer documentation
├── LICENSE                            # MIT License
├── src/
│   └── reversal_autotheme/
│       ├── __init__.py                # Package metadata & version
│       ├── cli.py                     # Command-line interface & argument parser
│       ├── engine.py                  # Core squircle geometry, shadow & palette analysis
│       ├── discovery.py               # Desktop entry scanner, Steam/Flatpak resolver
│       ├── manifest.py                # Idempotency & pristine source management
│       └── desktop.py                 # Live desktop refresh & notification handler
├── data/
│   ├── reversal-autotheme.desktop     # Standard XDG desktop launcher entry
│   └── icons/
│       ├── reversal-autotheme.svg     # Official SVG app icon (macOS-style theme wand)
│       └── 512x512/
│           └── reversal-autotheme.png # High-res raster icon
└── packaging/
    ├── arch/
    │   └── PKGBUILD                   # Arch Linux / AUR package build definition
    ├── debian/
    │   ├── control                    # Debian/Ubuntu package metadata & dependencies
    │   ├── rules                      # Debian package build rules
    │   └── changelog                  # Debian changelog
    └── rpm/
        └── reversal-autotheme.spec    # Fedora / openSUSE RPM spec file
```

---

## Packaging & Export Strategy

1. **Universal Installer (`install.sh` & `Makefile`)**:
   - Allows users on any Linux distro to install with either:
     - `sudo ./install.sh` (System-wide: `/usr/local/bin`, `/usr/share/applications`, `/usr/share/icons`)
     - `./install.sh --user` (User-only: `~/.local/bin`, `~/.local/share/applications`)
2. **Arch Linux AUR (`PKGBUILD`)**:
   - Ready for Arch User Repository submission (`yay -S reversal-autotheme` or `makepkg -si`).
3. **Debian / Ubuntu (`.deb` Build Script)**:
   - Targets Debian, Ubuntu, Linux Mint, Pop!_OS.
4. **Fedora / openSUSE (`.spec` File)**:
   - RPM spec file for building with `rpmbuild` or COPR.
5. **Python Package (`pyproject.toml`)**:
   - Installable via `pip install .` or `pipx install .`.

---

## Proposed Changes

### [NEW] Project Directory: `/home/ausamnco/.gemini/antigravity/scratch/reversal-autotheme`

#### 1. Core Source Code (`src/reversal_autotheme/`)
- Modularize the single-file script into clean, reusable Python modules with type annotations and docstrings.

#### 2. Packaging Metadata & Configs
- `pyproject.toml`, `setup.py`, `Makefile`, `install.sh`.

#### 3. Packaging Files (`packaging/arch/PKGBUILD`, `packaging/debian/`, `packaging/rpm/`)
- Native package specifications for distribution package managers.

#### 4. Artwork & Desktop Integration
- High-res vector and raster app icons and desktop launcher.

#### 5. Documentation
- Full `README.md` with CLI options, screenshot references, installation instructions for each distro, and customization options.

---

## Verification Plan

### Automated Tests
1. **Repository & Packaging Validation**:
   - Test `pip install -e .` in virtual environment.
   - Run `python3 -m unittest` or module import checks.
2. **Universal Installer Test**:
   - Run `./install.sh --user` into temporary target prefix.
3. **Arch Linux PKGBUILD Validation**:
   - Validate PKGBUILD syntax with `namcap` (if available) or `makepkg --nobuild`.
4. **Desktop Entry Validation**:
   - Run `desktop-file-validate` on `data/reversal-autotheme.desktop`.
