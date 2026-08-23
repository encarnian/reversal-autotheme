# Reversal Auto-Theme 🪄

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](#installation)
[![Desktop](https://img.shields.io/badge/Desktop-GNOME%20%7C%20KDE%20%7C%20XFCE-brightgreen.svg)](#features)

**Reversal Auto-Theme** is an intelligent, universal icon theming engine for Linux desktop environments. It dynamically scans all installed desktop applications, detects applications lacking native icon theme coverage, and automatically generates pixel-perfect **macOS-style continuous squircle icons** with realistic drop shadows matching the [Reversal icon theme](https://github.com/yeyushengfan258/Reversal-icon-theme) specification.

---

## ✨ Features

- **Universal App Discovery**: Scans standard XDG application directories, Steam libraries, and Flatpaks.
- **Continuous macOS Squircle Geometry**: Implements standard Apple Big Sur+ continuous curvature squircle geometry (`rx="15" ry="15"` on 64x64 canvas / ~27% radius ratio) with soft Gaussian drop shadows.
- **Adaptive Visual Theming**:
  - **Full-Bleed / Square Apps**: Clips artwork cleanly into the squircle boundary (e.g. *Nuvio*, *OrcaSlicer*, *Furmark*, *Goverlay*, games).
  - **Transparent Logos / Glyphs**: Extracts dominant brand colors and centers the glyph at 70% scale on top of a complementary gradient base plate (e.g. *CoolerControl*, *Sunshine*, *Resources*, *OpenRGB*, *btop*, *Java*).
- **Pristine Source Isolation & Idempotency**: Automatically caches pristine original upstream assets and tracks SHA-256 hashes in `manifest.json`. Running the tool multiple times will never double-nest or degrade existing icons.
- **Live Desktop Refresh**: Automatically invalidates GNOME Shell, Dash to Dock, and GTK icon texture caches to immediately display updated icons on your screen without logging out.
- **One-Click Desktop Launcher**: Launchable directly from your application grid with desktop notification feedback.

---

## 🚀 Installation

### 1. Universal Installer (Any Linux Distro)

#### User-Only Installation (Recommended)
```bash
git clone https://github.com/reversal-icon-theme/reversal-autotheme.git
cd reversal-autotheme
./install.sh --user
```

#### System-Wide Installation
```bash
sudo ./install.sh
```

---

### 2. Arch Linux / AUR (Arch, Manjaro, CachyOS, EndeavourOS)

```bash
cd packaging/arch
makepkg -si
```
*(Or via AUR helper once published: `yay -S reversal-autotheme`)*

---

### 3. Debian / Ubuntu / Linux Mint / Pop!_OS

```bash
sudo apt install python3-pil python3-numpy librsvg2-bin libnotify-bin
sudo make install
```

---

### 4. Fedora / openSUSE / RHEL

```bash
sudo dnf install python3-pillow python3-numpy librsvg2-tools libnotify
sudo make install
```

---

### 5. Python / pipx

```bash
pipx install .
```

---

## 🛠️ Usage

### From Application Menu
Open your application launcher and click on **`Reversal Auto-Theme`**. It will automatically scan your applications, generate any missing squircle icons, refresh your desktop, and display a completion notification.

### From Command Line

```bash
# Auto-theme all detected unthemed applications
reversal-autotheme --all

# Include desktop notifications
reversal-autotheme --all --notify

# List all applications needing squircle icons without making changes
reversal-autotheme --list

# Theme a specific application or icon by name
reversal-autotheme --app nuvio

# Force re-generation of all icons
reversal-autotheme --all --force
```

---

## 📂 Project Architecture

```text
reversal-autotheme/
├── pyproject.toml                     # Modern PEP 621 Python packaging configuration
├── setup.py                           # Legacy setuptools build script
├── Makefile                           # Universal cross-platform build & install recipes
├── install.sh                         # Interactive / automated installer script
├── src/
│   └── reversal_autotheme/
│       ├── __init__.py                # Package version and metadata
│       ├── cli.py                     # Command-line interface & argument parser
│       ├── engine.py                  # Core squircle geometry, shadow & palette analysis
│       ├── discovery.py               # Desktop entry scanner, Steam/Flatpak resolver
│       ├── manifest.py                # Idempotency & pristine source management
│       └── desktop.py                 # Live desktop refresh & notification handler
├── data/
│   ├── reversal-autotheme.desktop     # XDG desktop launcher entry
│   └── icons/
│       ├── reversal-autotheme.svg     # Official SVG app icon
│       └── 512x512/
│           └── reversal-autotheme.png # High-res raster icon
└── packaging/
    ├── arch/PKGBUILD                  # Arch Linux PKGBUILD
    ├── debian/                        # Debian/Ubuntu control, rules, changelog
    └── rpm/reversal-autotheme.spec    # Fedora/RHEL RPM spec
```

---

## 🧪 Testing

Run test suite:
```bash
make test
# Or with Python directly:
python3 -m unittest discover tests
```

---

## 🤝 Contributing

Contributions, bug reports, and pull requests are welcome on GitHub!

---

## 📄 License

Distributed under the [MIT License](LICENSE).
