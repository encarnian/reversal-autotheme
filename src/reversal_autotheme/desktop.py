"""
Desktop Integration, Theme Asset Distribution, and Live Refresh Engine
Handles installing SVG wrappers into all Reversal themes, rebuilding icon caches,
and triggering instantaneous live GNOME Shell & Dash to Dock redraws.
"""

import os
import time
import glob
import subprocess
from typing import List
from PIL import Image
from .engine import generate_svg_wrapper


def get_reversal_dirs() -> List[str]:
    """Find all Reversal icon theme directories installed on the system."""
    candidates = (
        glob.glob(os.path.expanduser('~/.local/share/icons/Reversal*')) +
        glob.glob(os.path.expanduser('~/.icons/Reversal*')) +
        glob.glob('/usr/share/icons/Reversal*')
    )
    return sorted(list(set([d for d in candidates if os.path.isdir(d)])))


def get_native_reversal_icons(generated_aliases: set) -> set:
    """Collect native icon base names present across Reversal themes."""
    icon_names = set()
    for theme_dir in get_reversal_dirs():
        scalable = os.path.join(theme_dir, 'apps', 'scalable')
        if os.path.exists(scalable):
            for f in os.listdir(scalable):
                if f.endswith('.svg') or f.endswith('.png'):
                    name = os.path.splitext(f)[0]
                    if name not in generated_aliases:
                        icon_names.add(name)
    return icon_names


def install_icon_to_reversal(icon_name: str, final_img: Image.Image, aliases: List[str] = None):
    """Installs the generated squircle icon into all installed Reversal themes."""
    if aliases is None:
        aliases = []
    all_names = list(set([icon_name] + [a for a in aliases if a]))

    reversal_dirs = get_reversal_dirs()
    svg_wrapper = generate_svg_wrapper(final_img)

    for theme_dir in reversal_dirs:
        # Check permissions for system directory
        if not os.access(theme_dir, os.W_OK):
            continue
        scalable_dir = os.path.join(theme_dir, 'apps', 'scalable')
        os.makedirs(scalable_dir, exist_ok=True)

        for name in all_names:
            svg_path = os.path.join(scalable_dir, f"{name}.svg")
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_wrapper)


def update_icon_caches():
    """Rebuilds GTK icon caches, refreshes desktop database, and triggers live GNOME reload."""
    dirs_to_update = get_reversal_dirs()
    for d in dirs_to_update:
        if os.path.exists(d) and os.access(d, os.W_OK):
            try:
                subprocess.run(['gtk-update-icon-cache', '-f', '-t', d],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    # Refresh desktop database
    user_apps = os.path.expanduser('~/.local/share/applications')
    if os.path.exists(user_apps):
        subprocess.run(['update-desktop-database', user_apps],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Force GNOME Shell live reload
    try:
        current = subprocess.check_output(
            ['gsettings', 'get', 'org.gnome.desktop.interface', 'icon-theme']
        ).decode().strip().strip("'")
        if current:
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'icon-theme', 'hicolor'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.12)
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'icon-theme', current],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def send_notification(title: str, message: str, icon: str = "preferences-desktop-theme", critical: bool = False):
    """Sends desktop notification via notify-send if available."""
    urgency = "critical" if critical else "normal"
    try:
        subprocess.run(['notify-send', '-u', urgency, '-i', icon, title, message],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
