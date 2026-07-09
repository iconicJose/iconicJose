from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "iconic-jose-particle-banner.gif"

WIDTH = 1000
HEIGHT = 250
SCALE = 2
FRAMES = 180
FRAME_MS = 50
CONNECT_DISTANCE = 132
PARTICLE_RADIUS = 4
MARGIN = 14

COLORS = [
    (239, 68, 68),
    (168, 85, 247),
    (34, 197, 94),
    (234, 179, 8),
    (6, 182, 212),
    (20, 184, 166),
    (249, 115, 22),
    (56, 189, 248),
    (132, 204, 22),
    (236, 72, 153),
    (147, 51, 234),
    (14, 165, 233),
    (245, 158, 11),
    (16, 185, 129),
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


TITLE_FONT = font(r"C:\Windows\Fonts\segoeui.ttf", 56)
SOCIAL_FONT = font(r"C:\Windows\Fonts\segoeui.ttf", 18)


def text_size(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font_obj)
    return box[2] - box[0], box[3] - box[1]


def make_particles() -> list[dict[str, object]]:
    random.seed(17)
    particles: list[dict[str, object]] = []
    for i in range(18):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(0.55, 1.15)
        particles.append(
            {
                "x": random.uniform(MARGIN, WIDTH - MARGIN),
                "y": random.uniform(MARGIN, HEIGHT - MARGIN),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": COLORS[i % len(COLORS)],
                "r": random.uniform(3.0, 4.8),
            }
        )
    return particles


def step(particles: list[dict[str, object]]) -> None:
    for p in particles:
        x = float(p["x"]) + float(p["vx"])
        y = float(p["y"]) + float(p["vy"])
        r = float(p["r"])

        if x < MARGIN + r:
            x = MARGIN + r
            p["vx"] = abs(float(p["vx"]))
        elif x > WIDTH - MARGIN - r:
            x = WIDTH - MARGIN - r
            p["vx"] = -abs(float(p["vx"]))

        if y < MARGIN + r:
            y = MARGIN + r
            p["vy"] = abs(float(p["vy"]))
        elif y > HEIGHT - MARGIN - r:
            y = HEIGHT - MARGIN - r
            p["vy"] = -abs(float(p["vy"]))

        p["x"] = x
        p["y"] = y


def draw_frame(particles: list[dict[str, object]]) -> Image.Image:
    canvas = Image.new("RGBA", (WIDTH * SCALE, HEIGHT * SCALE), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas, "RGBA")

    scaled = [
        {
            "x": float(p["x"]) * SCALE,
            "y": float(p["y"]) * SCALE,
            "r": float(p["r"]) * SCALE,
            "color": p["color"],
        }
        for p in particles
    ]

    for i, a in enumerate(scaled):
        for b in scaled[i + 1 :]:
            dx = float(a["x"]) - float(b["x"])
            dy = float(a["y"]) - float(b["y"])
            distance = math.hypot(dx, dy) / SCALE
            if distance <= CONNECT_DISTANCE:
                alpha = int(118 * (1 - distance / CONNECT_DISTANCE))
                draw.line(
                    (a["x"], a["y"], b["x"], b["y"]),
                    fill=(136, 144, 158, alpha),
                    width=1 * SCALE,
                )

    for p in scaled:
        x = float(p["x"])
        y = float(p["y"])
        r = float(p["r"])
        color = tuple(p["color"])  # type: ignore[arg-type]
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, 235))

    title = "Iconic Jose"
    title_w, title_h = text_size(draw, title, TITLE_FONT)
    title_x = (WIDTH * SCALE - title_w) // 2
    title_y = 74 * SCALE
    contact_x = title_x + 5 * SCALE
    contact_y = 144 * SCALE

    panel_pad_x = 26 * SCALE
    panel_pad_y = 22 * SCALE
    panel = (
        title_x - panel_pad_x,
        title_y - panel_pad_y,
        title_x + title_w + panel_pad_x,
        contact_y + 78 * SCALE,
    )
    draw.rounded_rectangle(panel, radius=18 * SCALE, fill=(255, 255, 255, 232))

    draw.text((title_x, title_y), title, fill=(7, 17, 31, 255), font=TITLE_FONT)
    socials = ["Insta: J0sewho", "Snapchat: Iconic-jose", "TikTok: Ban.jose"]
    for idx, line in enumerate(socials):
        draw.text((contact_x, contact_y + idx * 28 * SCALE), line, fill=(17, 24, 39, 255), font=SOCIAL_FONT)

    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("P", palette=Image.Palette.ADAPTIVE)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    particles = make_particles()
    frames = []
    for _ in range(FRAMES):
        frames.append(draw_frame(particles))
        step(particles)

    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(OUT)


if __name__ == "__main__":
    main()
