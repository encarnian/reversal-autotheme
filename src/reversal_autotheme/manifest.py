"""
Pristine Source Isolation & Idempotency Manifest Manager
Prevents recursive nesting by saving original source assets and tracking SHA-256 checksums.
"""

import os
import json
import hashlib
import shutil
from typing import Dict, Any, Optional

DATA_DIR = os.path.expanduser('~/.local/share/reversal-autotheme')
ORIGINALS_DIR = os.path.join(DATA_DIR, 'originals')
MANIFEST_FILE = os.path.join(DATA_DIR, 'manifest.json')


def ensure_dirs():
    os.makedirs(ORIGINALS_DIR, exist_ok=True)


def load_manifest() -> Dict[str, Any]:
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {'apps': {}}


def save_manifest(manifest: Dict[str, Any]):
    ensure_dirs()
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)


def get_file_hash(filepath: str) -> Optional[str]:
    try:
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


def cache_original_source(app_id: str, src_path: str) -> str:
    """Copies a pristine original image into the dedicated cache directory."""
    ensure_dirs()
    ext = os.path.splitext(src_path)[1]
    cached_path = os.path.join(ORIGINALS_DIR, f"{app_id}{ext}")
    if not os.path.exists(cached_path):
        try:
            shutil.copy2(src_path, cached_path)
        except Exception:
            pass
    return cached_path
