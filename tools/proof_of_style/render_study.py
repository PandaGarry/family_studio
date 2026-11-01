#!/usr/bin/env python3
"""Build a small local motion study from the user's existing child references.

This is a 2.5D cutout/pose-blocking preview, not a final rig or Godot render.
Requires Pillow: python -m pip install Pillow
"""
from __future__ import annotations

import math
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
REFS = ROOT / "assets" / "references" / "raw"
ASSETS = ROOT / "assets" / "proof_of_style"
OUTPUT = ROOT / "artifacts" / "proof-of-style"
WIDTH, HEIGHT = 720, 1280
FPS = 12.5
DURATION = 6.0
FRAMES = int(FPS * DURATION)


def key_green(path: Path, crop: tuple[int, int, int, int]) -> Image.Image:
    """Remove only the connected green backdrop, preserving green-tinted cloth."""
    image = Image.open(path).convert("RGBA").crop(crop)
    width, height = image.size
    pixels = image.load()
    screen = Image.new("L", (width, height), 0)
    screen_px = screen.load()

    def is_backdrop(x: int, y: int) -> bool:
        r, g, b, _ = pixels[x, y]
        # The studio green is dark-red / high-green / low-blue. Requiring it to
        # be connected to the crop edge protects the pale mint cap from keying.
        return r < 52 and g > 88 and b < 118 and g - max(r, b) > 42

    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        if is_backdrop(x, 0):
            screen_px[x, 0] = 255
            queue.append((x, 0))
        if is_backdrop(x, height - 1) and not screen_px[x, height - 1]:
            screen_px[x, height - 1] = 255
            queue.append((x, height - 1))
    for y in range(height):
        if is_backdrop(0, y) and not screen_px[0, y]:
            screen_px[0, y] = 255
            queue.append((0, y))
        if is_backdrop(width - 1, y) and not screen_px[width - 1, y]:
            screen_px[width - 1, y] = 255
            queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and not screen_px[nx, ny] and is_backdrop(nx, ny):
                screen_px[nx, ny] = 255
                queue.append((nx, ny))

    # Expand the keyed backdrop by a pixel to suppress the green fringe, then
    # soften only the silhouette edge. Interior green reflections remain intact.
    expanded = screen.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.45))
    alpha = Image.eval(expanded, lambda value: 255 - value)
    for y in range(height):
        for x in range(width):
            r, g, b, _ = pixels[x, y]
            a = alpha.getpixel((x, y))
            if a < 255 and g > max(r, b):
                neutral = max(r, b)
                g = int(neutral + (g - neutral) * a / 255)
            pixels[x, y] = (r, g, b, a)

    image.putalpha(alpha)
    bbox = alpha.point(lambda a: 255 if a > 16 else 0).getbbox()
    if bbox is None:
        raise ValueError(f"No character silhouette found in {path.name}")
    return image.crop(bbox)


def make_closed_eye_variant(sprite: Image.Image) -> Image.Image:
    """Draw a single blink pose over the neutral front-facing source sprite."""
    # Coordinates are in the trimmed front-facing cutout: the eyes are around
    # y=165 after the green-screen margins have been removed. Use sampled lower-
    # lid skin as a soft patch, then add simple curved lids.
    blink = sprite.copy().convert("RGBA")
    original = sprite.convert("RGBA")
    draw = ImageDraw.Draw(blink)
    eye_boxes = [(102, 143, 158, 179), (190, 143, 246, 179)]
    source_pixels = original.load()
    for x1, y1, x2, y2 in eye_boxes:
        patch = Image.new("RGBA", (x2 - x1, y2 - y1), (0, 0, 0, 0))
        patch_pixels = patch.load()
        for py in range(patch.height):
            for px in range(patch.width):
                sx = min(max(x1 + px, 0), original.width - 1)
                sy = min(max(y1 + py + 34, 0), original.height - 1)
                r, g, b, _ = source_pixels[sx, sy]
                patch_pixels[px, py] = (r, g, b, 255)
        mask = Image.new("L", patch.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 2, patch.width - 1, patch.height - 2), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(0.8))
        blink.alpha_composite(Image.composite(patch, Image.new("RGBA", patch.size), mask), (x1, y1))
        draw = ImageDraw.Draw(blink)
        for i in range(25):
            t = i / 24
            x = x1 + 5 + t * (patch.width - 10)
            y = y1 + 22 - 7 * math.sin(math.pi * t)
            draw.ellipse((x - 1.4, y - 1.4, x + 1.4, y + 1.4), fill=(93, 58, 47, 255))
    return blink


def resize_height(image: Image.Image, height: int) -> Image.Image:
    width = round(image.width * height / image.height)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def gradient_background(t: float) -> Image.Image:
    """A small layered garden plate with gentle parallax in the hills."""
    strip = Image.new("RGB", (1, HEIGHT))
    top = (206, 235, 231)
    bottom = (113, 177, 125)
    for y in range(HEIGHT):
        q = y / (HEIGHT - 1)
        q = q * q * (3 - 2 * q)
        color = tuple(round(top[i] * (1 - q) + bottom[i] * q) for i in range(3))
        strip.putpixel((0, y), color)
    image = strip.resize((WIDTH, HEIGHT))

    draw = ImageDraw.Draw(image, "RGBA")
    # Far hills: slow drift gives a sense of depth without distracting from the face.
    drift = math.sin(t * 0.7) * 12
    draw.ellipse((-260 + drift, 390, 520 + drift, 810), fill=(121, 181, 151, 155))
    draw.ellipse((260 - drift * 0.65, 360, 1010 - drift * 0.65, 825), fill=(91, 158, 123, 175))
    draw.rectangle((0, 710, WIDTH, HEIGHT), fill=(111, 171, 111, 255))
    draw.ellipse((-110 - drift, 615, 405 - drift, 890), fill=(76, 145, 97, 220))
    draw.ellipse((390 + drift, 600, 870 + drift, 900), fill=(65, 135, 87, 230))

    # Mid-ground trees are deliberately soft, rounded masses.
    tree_shift = math.sin(t * 1.1) * 7
    for x, y, r, color in [
        (75, 650, 78, (65, 128, 85, 225)),
        (640, 625, 92, (71, 137, 88, 225)),
        (520, 690, 54, (81, 145, 96, 230)),
    ]:
        xx = x + tree_shift * (0.5 if x < WIDTH / 2 else -0.5)
        draw.rounded_rectangle((xx - 9, y + 50, xx + 10, 830), radius=7, fill=(111, 95, 69, 220))
        draw.ellipse((xx - r, y - r, xx + r, y + r), fill=color)
        draw.ellipse((xx - r * 0.68, y - r * 1.25, xx + r * 0.58, y + r * 0.25), fill=(92, 156, 106, 170))

    # Soft, low-contrast bokeh.
    for i, (x, y, r) in enumerate([(105, 350, 18), (590, 300, 12), (500, 470, 9), (230, 520, 7)]):
        pulse = 0.65 + 0.35 * math.sin(t * 1.8 + i)
        alpha = int(34 * pulse)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 250, 208, alpha))
    return image


def draw_firefly(frame: Image.Image, t: float) -> tuple[float, float]:
    """A small moving warm light; returns its screen location for character staging."""
    draw = ImageDraw.Draw(frame, "RGBA")
    if t < 0.45:
        return -40, 0
    progress = min(1.0, max(0.0, (t - 0.45) / 4.8))
    x = -25 + progress * 670
    # Keep the glint above the character's eyes; it should guide the gaze,
    # not obscure the face in this first test.
    y = 255 - 56 * math.sin(progress * math.pi) + 14 * math.sin(t * 3.4)
    radius = 9 + 2 * math.sin(t * 7)
    glow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((x - 34, y - 34, x + 34, y + 34), fill=(255, 224, 112, 105))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    frame.alpha_composite(glow)
    draw = ImageDraw.Draw(frame, "RGBA")
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 248, 202, 255))
    draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 255, 245, 255))
    # A few restrained trailing specks.
    for k in range(1, 4):
        lag = k * 13
        a = max(20, 115 - k * 30)
        draw.ellipse((x - lag - 2, y + k * 3 - 2, x - lag + 2, y + k * 3 + 2), fill=(255, 239, 164, a))
    return x, y


def place_character(
    frame: Image.Image,
    neutral: Image.Image,
    blink: Image.Image,
    pointing: Image.Image,
    t: float,
) -> None:
    # A deliberately simple motion-blocking pass: breathing, anticipation,
    # pose cut to the user's pointing key pose, then a gentle camera push.
    if t < 2.45:
        pose = blink if 1.68 <= t <= 1.84 else neutral
        base_h = 760
        image = resize_height(pose, base_h)
        if 1.35 <= t < 2.0:
            lean = -1.0 - 1.3 * math.sin((t - 1.35) / 0.65 * math.pi)
            image = image.rotate(lean, resample=Image.Resampling.BICUBIC, expand=True)
        camera = 1.0 + max(0, t - 1.6) * 0.035
    else:
        image = resize_height(pointing, 870)
        camera = 1.0 + min(0.035, (t - 2.45) * 0.014)
        image = image.rotate(-0.4 + 0.45 * math.sin(t * 1.5), resample=Image.Resampling.BICUBIC, expand=True)

    image = image.resize((round(image.width * camera), round(image.height * camera)), Image.Resampling.LANCZOS)
    breathing = 1.0 + 0.006 * math.sin(t * math.pi * 1.25)
    image = image.resize((image.width, round(image.height * breathing)), Image.Resampling.LANCZOS)
    bob = round(4 * math.sin(t * math.pi * 1.25))
    x = (WIDTH - image.width) // 2 - round(12 * max(0, t - 1.5))
    y = 270 + bob - round(max(0, t - 2.45) * 7)

    # Soft contact shadow, kept separate from the sprite plane.
    shadow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_y = 1080 + bob
    shadow_draw.ellipse((195, shadow_y, 535, shadow_y + 34), fill=(32, 79, 49, 94))
    frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
    frame.alpha_composite(image, (x, y))


def render() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    # Crops focus on the front-facing child and the matching pointing pose;
    # originals are never altered.
    neutral = key_green(REFS / "IMG_5973.png", (90, 540, 460, 1440))
    pointing = key_green(REFS / "IMG_5979.png", (280, 500, 930, 1610))
    # Remove narrow green-screen fringe without changing the silhouette design.
    neutral.save(ASSETS / "child_front_neutral.png")
    pointing.save(ASSETS / "child_pointing_crop.png")
    blink = make_closed_eye_variant(neutral)

    frames_rgb: list[Image.Image] = []
    gif_frames: list[Image.Image] = []
    for index in range(FRAMES):
        t = index / FPS
        frame = gradient_background(t).convert("RGBA")
        place_character(frame, neutral, blink, pointing, t)
        # Draw the foreground after the puppet for a little depth/occlusion.
        foreground = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(foreground, "RGBA")
        sway = math.sin(t * 1.3) * 5
        d.ellipse((-100 + sway, 1042, 310 + sway, 1310), fill=(48, 123, 74, 255))
        d.ellipse((420 - sway, 1050, 830 - sway, 1320), fill=(39, 112, 66, 255))
        for i in range(11):
            x = (i * 79 + 28) % WIDTH
            h = 28 + (i * 17 % 42)
            d.line((x, 1170, x + math.sin(t * 1.4 + i) * 8, 1170 - h), fill=(197, 213, 124, 210), width=3)
        frame.alpha_composite(foreground)
        draw_firefly(frame, t)
        # A subtle edge vignette keeps the viewer's eye on the face.
        vignette = Image.new("L", (WIDTH, HEIGHT), 0)
        vd = ImageDraw.Draw(vignette)
        vd.ellipse((-80, -70, WIDTH + 80, HEIGHT + 70), fill=155)
        vignette = vignette.filter(ImageFilter.GaussianBlur(80))
        shade = Image.new("RGBA", frame.size, (25, 49, 46, 0))
        shade.putalpha(Image.eval(vignette, lambda v: 70 - int(v * 0.32)))
        frame.alpha_composite(shade)
        rgb_frame = frame.convert("RGB")
        frames_rgb.append(rgb_frame)
        gif_frames.append(rgb_frame.quantize(colors=256, method=Image.Quantize.FASTOCTREE))

    gif_path = OUTPUT / "child-motion-study.gif"
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=round(1000 / FPS),
        loop=0,
        optimize=True,
        disposal=2,
    )
    poster = OUTPUT / "child-motion-study-poster.png"
    frames_rgb[min(int(FPS * 3), len(frames_rgb) - 1)].save(poster, optimize=True)
    mp4_path = OUTPUT / "child-motion-study.mp4"
    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise RuntimeError("Install preview requirements: python -m pip install -r requirements-preview.txt") from exc

    writer = imageio_ffmpeg.write_frames(
        str(mp4_path),
        (WIDTH, HEIGHT),
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        fps=25,
        quality=8,
        codec="libx264",
        output_params=["-movflags", "+faststart"],
    )
    writer.send(None)
    for rgb_frame in frames_rgb:
        frame_bytes = rgb_frame.tobytes()
        writer.send(frame_bytes)
        writer.send(frame_bytes)
    writer.close()
    print(f"Wrote {gif_path}")
    print(f"Wrote {poster}")
    print(f"Wrote {mp4_path}")


if __name__ == "__main__":
    render()
