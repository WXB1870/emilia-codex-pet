#!/usr/bin/env python3
"""Install this one local pet with a backup; never modify global settings."""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

from atlas import validate


def install(source, destination, dry_run=False):
    source, destination = Path(source).resolve(), Path(destination).expanduser().resolve()
    metadata = json.loads((source / 'pet.json').read_text(encoding='utf-8'))
    sheet_name = metadata['spritesheetPath']
    if Path(sheet_name).name != sheet_name:
        raise ValueError('spritesheetPath must name one file within the pet directory')
    report = validate(source / sheet_name)
    if metadata.get('spriteVersionNumber') != report['spriteVersionNumber']:
        raise ValueError('Manifest version does not match the sprite layout')
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination directories must not overlap')
    result = {'destination': str(destination), 'dryRun': dry_run,
              'sha256': report['sha256'], 'backup': None}
    if dry_run:
        return result
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not destination.is_dir():
        raise ValueError('Destination exists and is not a directory')
    backup = None
    if destination.exists():
        backup = Path(tempfile.mkdtemp(prefix=destination.name + '.backup-', dir=destination.parent))
        shutil.copytree(destination, backup, dirs_exist_ok=True)
        result['backup'] = str(backup)
    stage = Path(tempfile.mkdtemp(prefix=destination.name + '.stage-', dir=destination.parent))
    try:
        if destination.exists():
            shutil.copytree(destination, stage, dirs_exist_ok=True)
        shutil.copy2(source / sheet_name, stage / sheet_name)
        shutil.copy2(source / 'pet.json', stage / 'pet.json')
        # Keep existing unrelated files, and replace only this pet's atlas and manifest.
        destination.mkdir(exist_ok=True)
        for name in (sheet_name, 'pet.json'):
            os.replace(stage / name, destination / name)
    except Exception:
        if backup is not None:
            shutil.copytree(backup, destination, dirs_exist_ok=True)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    return result


def main():
    root = Path(__file__).resolve().parents[1]
    codex_home = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')).expanduser()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=root / 'pet/emilia-anime')
    parser.add_argument('--destination', type=Path, default=codex_home / 'pets/emilia-anime')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        result = install(args.source, args.destination, args.dry_run)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        parser.exit(1, f'Error: {error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.dry_run:
        print('Installed. Refresh the pet settings and select Emilia manually.')


if __name__ == '__main__':
    main()
