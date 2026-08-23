import unittest
from PIL import Image
from reversal_autotheme.engine import (
    create_squircle_mask,
    create_shadow_layer,
    analyze_image_palette,
    generate_squircle_icon,
    CANVAS_SIZE
)

class TestEngine(unittest.TestCase):
    def test_mask_generation(self):
        mask = create_squircle_mask()
        self.assertEqual(mask.size, (CANVAS_SIZE, CANVAS_SIZE))
        self.assertEqual(mask.mode, 'L')

    def test_shadow_generation(self):
        shadow = create_shadow_layer()
        self.assertEqual(shadow.size, (CANVAS_SIZE, CANVAS_SIZE))
        self.assertEqual(shadow.mode, 'RGBA')

    def test_palette_classification(self):
        # Transparent image
        trans_img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        self.assertEqual(analyze_image_palette(trans_img), 'transparent_glyph')

        # Full bleed solid image
        full_img = Image.new('RGBA', (512, 512), (255, 0, 0, 255))
        self.assertEqual(analyze_image_palette(full_img), 'full_bleed')

    def test_generate_squircle_icon(self):
        src = Image.new('RGBA', (512, 512), (100, 150, 200, 255))
        icon = generate_squircle_icon(src)
        self.assertEqual(icon.size, (CANVAS_SIZE, CANVAS_SIZE))
        self.assertEqual(icon.mode, 'RGBA')

if __name__ == '__main__':
    unittest.main()
