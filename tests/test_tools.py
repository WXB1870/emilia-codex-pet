"""Safety and round-trip checks for the published tools."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import atlas
from install import install


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.source = ROOT / 'pet/emilia-anime'

    def tearDown(self):
        self.temp.cleanup()

    def test_dry_run_does_not_create_destination(self):
        destination = self.path / 'not-created' / 'pet'
        result = install(self.source, destination, dry_run=True)
        self.assertTrue(result['dryRun'])
        self.assertFalse(destination.parent.exists())

    def test_existing_pet_backed_up_and_global_config_untouched(self):
        config = self.path / 'config.toml'
        config.write_text('[desktop]\nselected-avatar-id = "existing-pet"\n')
        destination = self.path / 'pets/emilia-anime'
        destination.mkdir(parents=True)
        (destination / 'pet.json').write_text('{"old": true}\n')
        (destination / 'custom-notes.txt').write_text('keep this')
        before = config.read_bytes()
        result = install(self.source, destination)
        backup = Path(result['backup'])
        self.assertEqual(json.loads((backup / 'pet.json').read_text()), {'old': True})
        self.assertEqual((destination / 'custom-notes.txt').read_text(), 'keep this')
        self.assertEqual(config.read_bytes(), before)
        self.assertEqual((destination / 'spritesheet.png').read_bytes(),
                         (self.source / 'spritesheet.png').read_bytes())

    def test_extract_build_preserves_all_pixels(self):
        source = self.source / 'spritesheet.png'
        frames = self.path / 'frames'
        atlas.extract(source, frames)
        output = self.path / 'rebuilt.png'
        report = atlas.build(frames, output)
        self.assertEqual(report['requiredFrames'], 73)
        self.assertEqual(Image.open(source).convert('RGBA').tobytes(),
                         Image.open(output).convert('RGBA').tobytes())

    def test_rejects_art_in_unused_cell(self):
        image = Image.open(self.source / 'spritesheet.png').convert('RGBA')
        image.putpixel((7 * 192 + 10, 10), (255, 0, 0, 255))
        bad = self.path / 'unused-cell.png'
        image.save(bad)
        with self.assertRaisesRegex(ValueError, 'Unused cell'):
            atlas.validate(bad)

    def test_rejects_empty_required_frame(self):
        image = Image.open(self.source / 'spritesheet.png').convert('RGBA')
        image.paste((0, 0, 0, 0), (0, 0, 192, 208))
        bad = self.path / 'empty-frame.png'
        image.save(bad)
        with self.assertRaisesRegex(ValueError, 'Missing frame'):
            atlas.validate(bad)


if __name__ == '__main__':
    unittest.main()
