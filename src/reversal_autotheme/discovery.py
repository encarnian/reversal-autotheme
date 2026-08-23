"""
Desktop Application & Pristine Source Icon Discovery
Scans XDG desktop entries, Steam library caches, and Flatpak manifests.
"""

import os
import glob
import configparser
from typing import List, Dict, Any, Optional
from .manifest import ORIGINALS_DIR


def discover_desktop_apps() -> List[Dict[str, Any]]:
    """Scans all system and user XDG application entries."""
    desktop_patterns = [
        '/usr/share/applications/*.desktop',
        os.path.expanduser('~/.local/share/applications/*.desktop'),
        '/var/lib/flatpak/exports/share/applications/*.desktop',
        os.path.expanduser('~/.local/share/flatpak/exports/share/applications/*.desktop')
    ]
    files = []
    for pat in desktop_patterns:
        files.extend(glob.glob(pat))

    apps = []
    for df in files:
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        try:
            cp.read(df, encoding='utf-8')
            if not cp.has_section('Desktop Entry'):
                continue
            if cp.getboolean('Desktop Entry', 'NoDisplay', fallback=False):
                continue
            icon = cp.get('Desktop Entry', 'Icon', fallback=None)
            name = cp.get('Desktop Entry', 'Name', fallback=os.path.basename(df))
            wm_class = cp.get('Desktop Entry', 'StartupWMClass', fallback=None)
            exec_cmd = cp.get('Desktop Entry', 'Exec', fallback=None)
            base_id = os.path.splitext(os.path.basename(df))[0]

            if icon:
                apps.append({
                    'desktop_file': df,
                    'name': name,
                    'icon': icon,
                    'wm_class': wm_class,
                    'exec': exec_cmd,
                    'id': base_id
                })
        except Exception:
            pass

    return apps


def find_pristine_source(icon_name: str, app_id: str, desktop_file_path: Optional[str] = None) -> Optional[str]:
    """Finds the pristine original upstream source icon. Strictly avoids generated icon themes."""
    if not icon_name:
        return None

    # 1. Check if we already cached a pristine original
    cached_candidates = (
        glob.glob(os.path.join(ORIGINALS_DIR, f"{app_id}.*")) +
        glob.glob(os.path.join(ORIGINALS_DIR, f"{icon_name}.*"))
    )
    for c in cached_candidates:
        if os.path.exists(c) and os.path.getsize(c) > 0:
            return c

    # 2. Check if direct absolute path exists
    if os.path.isabs(icon_name):
        orig_cand = icon_name + '.orig'
        if os.path.exists(orig_cand):
            return orig_cand
        if os.path.exists(icon_name):
            return icon_name

    # Check if .orig exists in desktop directory or heroic
    if 'heroic' in str(desktop_file_path).lower() or 'heroic' in icon_name.lower():
        heroic_cands = glob.glob(os.path.expanduser(f'~/.config/heroic/icons/*{icon_name}*.orig'))
        for hc in heroic_cands:
            if os.path.exists(hc):
                return hc

    # 3. System Search Locations (STRICTLY SYSTEM, never user theme directories)
    search_dirs = [
        '/usr/share/icons/hicolor/scalable/apps',
        '/usr/share/icons/hicolor/512x512/apps',
        '/usr/share/icons/hicolor/256x256/apps',
        '/usr/share/icons/hicolor/192x192/apps',
        '/usr/share/icons/hicolor/128x128/apps',
        '/usr/share/icons/hicolor/96x96/apps',
        '/usr/share/icons/hicolor/64x64/apps',
        '/usr/share/icons/hicolor/48x48/apps',
        '/usr/share/icons/hicolor/32x32/apps',
        '/usr/share/pixmaps',
        '/var/lib/flatpak/exports/share/icons/hicolor/scalable/apps',
        '/var/lib/flatpak/exports/share/icons/hicolor/512x512/apps',
        '/opt/nuvio-linux/lib',
        os.path.expanduser('~/.local/share/flatpak/exports/share/icons/hicolor/scalable/apps'),
    ]

    extensions = ['.svg', '.png', '.jpg', '.jpeg', '.xpm', '']
    for d in search_dirs:
        if not os.path.exists(d):
            continue
        for ext in extensions:
            target = os.path.join(d, icon_name + ext)
            if os.path.exists(target) and os.path.isfile(target):
                return target

    # 4. Check Steam games cache
    if icon_name.startswith('steam_icon_'):
        appid = icon_name.replace('steam_icon_', '')
        steam_paths = [
            os.path.expanduser(f'~/.steam/steam/steam/games/{appid}.ico'),
            os.path.expanduser(f'~/.local/share/Steam/steam/games/{appid}.ico'),
            os.path.expanduser(f'~/.local/share/icons/hicolor/32x32/apps/steam_icon_{appid}.png'),
            os.path.expanduser(f'~/.local/share/icons/hicolor/256x256/apps/steam_icon_{appid}.png'),
        ]
        for sp in steam_paths:
            if os.path.exists(sp):
                return sp

    # 5. User hicolor fallback
    user_hicolor_dirs = [
        os.path.expanduser('~/.local/share/icons/hicolor/256x256/apps'),
        os.path.expanduser('~/.local/share/icons/hicolor/128x128/apps'),
        os.path.expanduser('~/.local/share/icons/hicolor/scalable/apps'),
    ]
    for d in user_hicolor_dirs:
        if not os.path.exists(d):
            continue
        for ext in extensions:
            target = os.path.join(d, icon_name + ext)
            if os.path.exists(target) and os.path.isfile(target):
                return target

    return None
