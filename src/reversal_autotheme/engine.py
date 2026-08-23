"""
Reversal Auto-Theme Core Engine
Implements continuous macOS squircle geometry, realistic drop shadows,
palette extraction, and adaptive glyph-on-plate synthesis.
"""

import base64
import subprocess
from io import BytesIO
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Geometric Constants (Reversal 512x512 canvas specification)
CANVAS_SIZE = 512
MARGIN = 36          # 4.5 / 64 * 512 = 36px margin
SQUIRCLE_SIZE = CANVAS_SIZE - 2 * MARGIN  # 440px
CORNER_RADIUS = int(SQUIRCLE_SIZE * (15.0 / 55.0))  # 120px continuous curvature
SHADOW_OFFSET = 8    # 8px downward displacement
SHADOW_BLUR = 10     # Gaussian blur standard deviation
SHADOW_OPACITY = 75  # ~30% alpha for black drop shadow


def rasterize_svg(svg_path: str, size: int = CANVAS_SIZE) -> Optional[Image.Image]:
    """Rasterize an SVG vector file to a high-res RGBA PIL Image."""
    try:
        cmd = ['rsvg-convert', '-w', str(size), '-h', str(size), '-f', 'png', svg_path]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return Image.open(BytesIO(proc.stdout)).convert('RGBA')
    except Exception:
        pass

    try:
        cmd = ['magick', '-background', 'none', '-density', '300', svg_path, '-resize', f'{size}x{size}', 'png:-']
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return Image.open(BytesIO(proc.stdout)).convert('RGBA')
    except Exception:
        return None


def load_source_image(file_path: str, size: int = CANVAS_SIZE) -> Optional[Image.Image]:
    """Load image from filesystem, converting SVG if necessary and center-cropping to square."""
    if file_path.lower().endswith('.svg'):
        return rasterize_svg(file_path, size)
    try:
        img = Image.open(file_path).convert('RGBA')
        w, h = img.size
        if w != h:
            min_dim = min(w, h)
            left = (w - min_dim) // 2
            top = (h - min_dim) // 2
            img = img.crop((left, top, left + min_dim, top + min_dim))
        if img.size != (size, size):
            img = img.resize((size, size), Image.Resampling.LANCZOS)
        return img
    except Exception:
        return None


def create_squircle_mask(size: int = CANVAS_SIZE, margin: int = MARGIN, radius: int = CORNER_RADIUS) -> Image.Image:
    """Creates a high-precision 4x-supersampled antialiased squircle mask."""
    scale = 4
    big_size = size * scale
    big_margin = margin * scale
    big_radius = radius * scale

    mask = Image.new('L', (big_size, big_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [big_margin, big_margin, big_size - big_margin, big_size - big_margin],
        radius=big_radius,
        fill=255
    )
    return mask.resize((size, size), Image.Resampling.LANCZOS)


def create_shadow_layer(size: int = CANVAS_SIZE, margin: int = MARGIN, radius: int = CORNER_RADIUS,
                        offset: int = SHADOW_OFFSET, blur: int = SHADOW_BLUR,
                        opacity: int = SHADOW_OPACITY) -> Image.Image:
    """Creates a natural macOS-style drop shadow layer beneath the squircle."""
    shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle(
        [margin, margin + offset, size - margin, size - margin + offset],
        radius=radius,
        fill=(0, 0, 0, opacity)
    )
    return shadow.filter(ImageFilter.GaussianBlur(blur))


def analyze_image_palette(img: Image.Image) -> str:
    """Classify image as 'transparent_glyph', 'solid_bg_logo', or 'full_bleed'."""
    arr = np.array(img)
    h, w, c = arr.shape

    # Sample corners (15x15 pixel patches)
    corner_samples = np.concatenate([
        arr[0:15, 0:15],
        arr[0:15, -15:],
        arr[-15:, 0:15],
        arr[-15:, -15:]
    ], axis=0).reshape(-1, c)

    if c == 4:
        avg_corner_alpha = np.mean(corner_samples[:, 3])
        if avg_corner_alpha < 50:
            return 'transparent_glyph'

    rgb_corners = corner_samples[:, :3]
    corner_std = np.std(rgb_corners, axis=0).mean()
    corner_mean = np.mean(rgb_corners, axis=0)

    center = arr[h // 4:3 * h // 4, w // 4:3 * w // 4, :3]
    center_diff = np.mean(np.abs(center - corner_mean))

    if corner_std < 10 and center_diff > 25:
        return 'solid_bg_logo'

    return 'full_bleed'


def make_gradient_plate(width: int, height: int, radius: int,
                        color_top: Tuple[int, int, int],
                        color_bottom: Tuple[int, int, int]) -> Image.Image:
    """Generates an antialiased squircle plate with subtle vertical gradient."""
    plate = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    for y in range(height):
        ratio = y / max(1, height - 1)
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        for x in range(width):
            plate.putpixel((x, y), (r, g, b, 255))

    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)

    out = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    out.paste(plate, (0, 0), mask)
    return out


def generate_squircle_icon(src_img: Image.Image) -> Image.Image:
    """Processes any raw source image into a single-layer Reversal macOS squircle icon."""
    canvas = Image.new('RGBA', (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))

    # 1. Base Drop Shadow
    shadow = create_shadow_layer()
    canvas.paste(shadow, (0, 0), shadow)

    # 2. Process content based on classification
    kind = analyze_image_palette(src_img)
    squircle_mask = create_squircle_mask()

    if kind == 'full_bleed':
        fitted = src_img.resize((CANVAS_SIZE, CANVAS_SIZE), Image.Resampling.LANCZOS)
        canvas.paste(fitted, (0, 0), squircle_mask)

    elif kind == 'solid_bg_logo':
        arr = np.array(src_img)
        bg = arr[0, 0, :3]
        diff = np.sqrt(np.sum((arr[:, :, :3].astype(float) - bg.astype(float)) ** 2, axis=-1))

        alpha = np.clip((diff - 8.0) / 18.0, 0.0, 1.0) * 255.0
        logo_arr = arr.copy()
        if logo_arr.shape[-1] == 3:
            logo_arr = np.dstack([logo_arr, alpha.astype(np.uint8)])
        else:
            logo_arr[:, :, 3] = alpha.astype(np.uint8)

        ys, xs = np.where(alpha > 15)
        if len(ys) > 50 and len(xs) > 50:
            logo_crop = Image.fromarray(logo_arr).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

            c_top = tuple(np.clip(bg.astype(int) + 12, 0, 255))
            c_bot = tuple(np.clip(bg.astype(int) - 5, 0, 255))
            plate = make_gradient_plate(SQUIRCLE_SIZE, SQUIRCLE_SIZE, CORNER_RADIUS, c_top, c_bot)
            canvas.paste(plate, (MARGIN, MARGIN), plate)

            max_logo_dim = int(SQUIRCLE_SIZE * 0.72)
            logo_crop.thumbnail((max_logo_dim, max_logo_dim), Image.Resampling.LANCZOS)
            lw, lh = logo_crop.size
            canvas.paste(logo_crop, ((CANVAS_SIZE - lw) // 2, (CANVAS_SIZE - lh) // 2), logo_crop)
        else:
            fitted = src_img.resize((CANVAS_SIZE, CANVAS_SIZE), Image.Resampling.LANCZOS)
            canvas.paste(fitted, (0, 0), squircle_mask)

    else:  # transparent_glyph
        arr = np.array(src_img)
        alpha = arr[:, :, 3]
        ys, xs = np.where(alpha > 10)

        if len(ys) > 10 and len(xs) > 10:
            glyph_crop = src_img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        else:
            glyph_crop = src_img

        glyph_arr = np.array(glyph_crop)
        if glyph_arr.shape[-1] == 4:
            active_pixels = glyph_arr[glyph_arr[:, :, 3] > 40][:, :3]
        else:
            active_pixels = glyph_arr.reshape(-1, 3)

        glyph_brightness = np.mean(active_pixels) if len(active_pixels) > 0 else 128

        if glyph_brightness < 70:
            c_top = (250, 250, 252)
            c_bot = (225, 228, 235)
        else:
            c_top = (38, 42, 53)
            c_bot = (22, 24, 30)

        plate = make_gradient_plate(SQUIRCLE_SIZE, SQUIRCLE_SIZE, CORNER_RADIUS, c_top, c_bot)
        canvas.paste(plate, (MARGIN, MARGIN), plate)

        max_dim = int(SQUIRCLE_SIZE * 0.68)
        glyph_crop.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        gw, gh = glyph_crop.size
        canvas.paste(glyph_crop, ((CANVAS_SIZE - gw) // 2, (CANVAS_SIZE - gh) // 2), glyph_crop)

    return canvas


def generate_svg_wrapper(png_image: Image.Image) -> str:
    """Encapsulates a high-res PNG within a scalable 64x64 SVG container."""
    buffer = BytesIO()
    png_image.save(buffer, format="PNG")
    b64_data = base64.b64encode(buffer.getvalue()).decode('ascii')

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" version="1.1" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <image width="64" height="64" preserveAspectRatio="none" xlink:href="data:image/png;base64,{b64_data}"/>
</svg>
'''
