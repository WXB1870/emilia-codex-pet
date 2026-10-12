#!/usr/bin/env python3
"""Validate, extract, build and preview a native pet atlas. MIT licensed."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

CELL = (192, 208)
STATES = [
    ('idle', 6, [1680, 660, 660, 840, 840, 1920]),
    ('running-right', 8, [120] * 7 + [220]),
    ('running-left', 8, [120] * 7 + [220]),
    ('waving', 4, [140] * 3 + [280]),
    ('jumping', 5, [140] * 4 + [280]),
    ('failed', 8, [140] * 7 + [240]),
    ('waiting', 6, [150] * 5 + [260]),
    ('running', 6, [120] * 5 + [220]),
    ('review', 6, [150] * 5 + [280]),
    ('look-0', 8, [160] * 8),
    ('look-1', 8, [160] * 8),
]


def validate(path):
    path = Path(path)
    if not 0 < path.stat().st_size <= 20 * 1024 * 1024:
        raise ValueError('Atlas must be between 1 byte and 20 MiB')
    with Image.open(path) as opened:
        if opened.format not in ('PNG', 'WEBP'):
            raise ValueError('Atlas must be PNG or WebP')
        if opened.size not in ((1536, 1872), (1536, 2288)):
            raise ValueError('Expected 1536x1872 (v1) or 1536x2288 (v2)')
        atlas = opened.convert('RGBA')
    rows = atlas.height // CELL[1]
    for row, (state, count, _) in enumerate(STATES[:rows]):
        for column in range(8):
            alpha = cell_at(atlas, row, column).getchannel('A')
            if column < count and alpha.getbbox() is None:
                raise ValueError(f'Missing frame: {state}/{column}')
            if column >= count and alpha.getbbox() is not None:
                raise ValueError(f'Unused cell is not transparent: row {row}, column {column}')
            if column < count and alpha.getextrema()[0] != 0:
                raise ValueError(f'Frame has no transparent background: {state}/{column}')
    return {
        'valid': True, 'width': atlas.width, 'height': atlas.height,
        'spriteVersionNumber': 2 if rows == 11 else 1,
        'requiredFrames': sum(count for _, count, _ in STATES[:rows]),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def cell_at(atlas, row, column):
    x, y = column * CELL[0], row * CELL[1]
    return atlas.crop((x, y, x + CELL[0], y + CELL[1]))


def extract(path, output):
    report = validate(path)
    output = Path(output)
    atlas = Image.open(path).convert('RGBA')
    rows = atlas.height // CELL[1]
    for row, (state, count, _) in enumerate(STATES[:rows]):
        folder = output / state
        folder.mkdir(parents=True, exist_ok=True)
        for column in range(count):
            cell_at(atlas, row, column).save(folder / f'{column:02d}.png')
    (output / 'layout.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def build(frames, output):
    frames, output = Path(frames), Path(output)
    layout = json.loads((frames / 'layout.json').read_text())
    version = layout.get('spriteVersionNumber')
    if version not in (1, 2):
        raise ValueError('Unsupported spriteVersionNumber')
    rows = 11 if version == 2 else 9
    atlas = Image.new('RGBA', (1536, rows * CELL[1]))
    for row, (state, count, _) in enumerate(STATES[:rows]):
        for column in range(count):
            with Image.open(frames / state / f'{column:02d}.png') as frame:
                if frame.size != CELL:
                    raise ValueError(f'{state}/{column} must be 192x208; no implicit rescaling')
                atlas.paste(frame.convert('RGBA'), (column * CELL[0], row * CELL[1]))
    output.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(output, format='PNG')
    return validate(output)


def preview(path, output):
    report = validate(path)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    atlas = Image.open(path).convert('RGBA')
    rows = atlas.height // CELL[1]
    groups = []
    for row, (state, count, durations) in enumerate(STATES[:rows]):
        images = []
        for column in range(count):
            canvas = Image.new('RGBA', CELL, (242, 240, 247, 255))
            canvas.alpha_composite(cell_at(atlas, row, column))
            images.append(canvas.convert('RGB'))
        save_gif(images, durations, output / f'{state}.gif')
        groups.append((images, durations))
    all_frames = [f for images, _ in groups[:9] for f in images]
    all_times = [t for _, durations in groups[:9] for t in durations]
    save_gif(all_frames, all_times, output / 'all-states.gif')
    idle, hover = groups[0], groups[4]
    save_gif(idle[0] + hover[0] * 3 + idle[0],
             idle[1] + hover[1] * 3 + idle[1], output / 'idle-hover-idle.gif')
    return report


def save_gif(images, durations, output):
    images[0].save(output, save_all=True, append_images=images[1:],
                   duration=durations, loop=0, disposal=2, optimize=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'extract', 'build', 'preview'])
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.command != 'validate' and args.output is None:
        parser.error('--output is required for this command')
    try:
        if args.command == 'validate':
            result = validate(args.input)
        else:
            result = globals()[args.command](args.input, args.output)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        parser.exit(1, f'Error: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
