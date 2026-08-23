"""
Command Line Interface for Reversal Auto-Theme
"""

import os
import sys
import time
import argparse
from typing import List

from . import __version__
from .manifest import load_manifest, save_manifest, get_file_hash, cache_original_source
from .discovery import discover_desktop_apps, find_pristine_source
from .engine import load_source_image, generate_squircle_icon
from .desktop import (
    get_native_reversal_icons,
    install_icon_to_reversal,
    update_icon_caches,
    send_notification
)


def run_autotheme(app_filter: str = None, force: bool = False, notify: bool = False, verbose: bool = True) -> int:
    """Core workflow execution."""
    if notify:
        send_notification("Reversal Auto-Theme", "Scanning applications and generating macOS-style squircle icons...")

    manifest = load_manifest()
    generated_aliases = set()
    for entry in manifest.get('apps', {}).values():
        for a in entry.get('aliases', []):
            generated_aliases.add(a)

    reversal_native_icons = get_native_reversal_icons(generated_aliases)
    apps = discover_desktop_apps()

    unthemed_apps = []
    for app in apps:
        icon_name = app['icon']
        is_abs = os.path.isabs(icon_name)

        # Check if already natively in Reversal (and not generated)
        if not is_abs and (icon_name in reversal_native_icons or (icon_name + '.svg') in reversal_native_icons):
            continue

        src_file = find_pristine_source(icon_name, app['id'], app['desktop_file'])
        if src_file:
            src_hash = get_file_hash(src_file)

            already_done = False
            if not force and app['id'] in manifest.get('apps', {}):
                recorded = manifest['apps'][app['id']]
                if recorded.get('source_hash') == src_hash:
                    already_done = True

            if not already_done:
                unthemed_apps.append((app, src_file, src_hash))

    if not unthemed_apps:
        if verbose:
            print("All applications are already up to date with macOS squircle icons. Nothing to do.")
        update_icon_caches()
        if notify:
            send_notification("Reversal Auto-Theme", "All application icons are already up to date!")
        return 0

    if verbose:
        print(f"Generating macOS-style squircle icons for {len(unthemed_apps)} application(s)...")

    processed_count = 0
    for app, src_file, src_hash in unthemed_apps:
        if app_filter and app_filter.lower() not in app['name'].lower() and app_filter.lower() not in app['icon'].lower():
            continue

        if verbose:
            print(f" -> Processing: {app['name']} (Source: {os.path.basename(src_file)})")

        cached_src = cache_original_source(app['id'], src_file)
        src_img = load_source_image(src_file)
        if src_img is None:
            continue

        final_squircle = generate_squircle_icon(src_img)

        icon_base = os.path.basename(app['icon'])
        icon_clean = os.path.splitext(icon_base)[0]

        aliases = [app['id'], icon_clean]
        if 'nuvio' in icon_clean.lower() or 'nuvio' in app['id'].lower():
            aliases.extend([
                'nuvio', 'nuvio-linux', 'nuvio-app-icon',
                'com-nuviolinux-app-MainKt', 'com.nuviolinux.app.MainKt',
                'com.nuvio.app.MainKt', 'com-nuvio-app-MainKt'
            ])

        if app['wm_class']:
            aliases.append(app['wm_class'])
            aliases.append(app['wm_class'].replace('-', '.'))
            aliases.append(app['wm_class'].replace('.', '-'))

        # Clean absolute paths in desktop entries if in user directory
        if os.path.isabs(app['icon']) and os.path.dirname(app['desktop_file']).startswith(os.path.expanduser('~')):
            clean_icon_ref = app['id']
            aliases.append(clean_icon_ref)
            try:
                with open(app['desktop_file'], 'r', encoding='utf-8') as f:
                    dcontent = f.read()
                lines = dcontent.splitlines()
                for idx, line in enumerate(lines):
                    if line.startswith('Icon='):
                        lines[idx] = f'Icon={clean_icon_ref}'
                with open(app['desktop_file'], 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines) + '\n')
            except Exception:
                pass

        install_icon_to_reversal(icon_clean, final_squircle, aliases=aliases)

        if 'apps' not in manifest:
            manifest['apps'] = {}
        manifest['apps'][app['id']] = {
            'name': app['name'],
            'icon': app['icon'],
            'source_file': src_file,
            'source_hash': src_hash,
            'aliases': aliases,
            'timestamp': time.time()
        }
        processed_count += 1

    save_manifest(manifest)
    if verbose:
        print(f"\nSuccessfully generated {processed_count} macOS squircle icons!")
        print("Updating GTK icon caches & live refreshing desktop...")
    update_icon_caches()
    if verbose:
        print("Desktop icon refresh complete.")

    if notify:
        send_notification("Reversal Auto-Theme", f"Successfully generated {processed_count} macOS squircle icons and refreshed desktop!")

    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="reversal-autotheme",
        description="Reversal Auto-Theme: Universal macOS Squircle Icon Generator for Linux Desktops"
    )
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('-a', '--all', action='store_true', help="Auto-theme all detected unthemed applications")
    parser.add_argument('-p', '--app', type=str, help="Process a specific application or icon name")
    parser.add_argument('-l', '--list', action='store_true', help="List all applications currently lacking squircle icons")
    parser.add_argument('-f', '--force', action='store_true', help="Re-generate icons even if already recorded in manifest")
    parser.add_argument('-n', '--notify', action='store_true', help="Show desktop notifications during operation")
    parser.add_argument('-q', '--quiet', action='store_true', help="Suppress console status output")

    args = parser.parse_args()

    if args.list:
        manifest = load_manifest()
        generated_aliases = set()
        for entry in manifest.get('apps', {}).values():
            for a in entry.get('aliases', []):
                generated_aliases.add(a)
        reversal_native_icons = get_native_reversal_icons(generated_aliases)
        apps = discover_desktop_apps()
        unthemed = []
        for app in apps:
            icon_name = app['icon']
            is_abs = os.path.isabs(icon_name)
            if not is_abs and (icon_name in reversal_native_icons or (icon_name + '.svg') in reversal_native_icons):
                continue
            src = find_pristine_source(icon_name, app['id'], app['desktop_file'])
            if src:
                src_hash = get_file_hash(src)
                if args.force or app['id'] not in manifest.get('apps', {}) or manifest['apps'][app['id']].get('source_hash') != src_hash:
                    unthemed.append((app, src))

        print(f"Found {len(unthemed)} application(s) needing squircle icons:")
        for app, src in unthemed:
            print(f" - {app['name']} (ID: {app['id']}, Icon: {app['icon']}) -> Source: {src}")
        return

    run_autotheme(
        app_filter=args.app,
        force=args.force,
        notify=args.notify,
        verbose=not args.quiet
    )


if __name__ == '__main__':
    main()
