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
CONNECT_DISTANCE = 56
MIN_SEPARATION = 58
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
    random.seed(31)
    particles: list[dict[str, object]] = []
    for i in range(30):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(0.72, 1.42)
        particle_rng = random.Random(900 + i * 37)
        for _ in range(120):
            x = random.uniform(MARGIN, WIDTH - MARGIN)
            y = random.uniform(MARGIN, HEIGHT - MARGIN)
            if all(math.hypot(x - float(p["x"]), y - float(p["y"])) > 36 for p in particles):
                break
        particles.append(
            {
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": COLORS[i % len(COLORS)],
                "r": random.uniform(3.0, 4.8),
                "angle": angle,
                "speed": speed,
                "turn": random.uniform(-0.075, 0.075),
                "phase": random.uniform(0, math.tau),
                "phase2": random.uniform(0, math.tau),
                "rng": particle_rng,
            }
        )
    return particles


def step(particles: list[dict[str, object]], frame: int) -> None:
    repel = [(0.0, 0.0) for _ in particles]

    for i, a in enumerate(particles):
        for j, b in enumerate(particles[i + 1 :], start=i + 1):
            dx = float(a["x"]) - float(b["x"])
            dy = float(a["y"]) - float(b["y"])
            distance = max(math.hypot(dx, dy), 0.001)
            if distance < MIN_SEPARATION:
                force = ((MIN_SEPARATION - distance) / MIN_SEPARATION) * 0.18
                nx = dx / distance
                ny = dy / distance
                ax, ay = repel[i]
                bx, by = repel[j]
                repel[i] = (ax + nx * force, ay + ny * force)
                repel[j] = (bx - nx * force, by - ny * force)

    for i, p in enumerate(particles):
        rng = p["rng"]
        assert isinstance(rng, random.Random)

        angle = float(p["angle"])
        speed = float(p["speed"])
        turn = float(p["turn"])
        phase = float(p["phase"])
        phase2 = float(p["phase2"])

        angle += (
            turn
            + math.sin(frame * 0.049 + phase) * 0.035
            + math.cos(frame * 0.031 + phase2) * 0.024
            + rng.uniform(-0.034, 0.034)
        )
        speed += math.sin(frame * 0.037 + phase2) * 0.01 + rng.uniform(-0.018, 0.018)
        speed = min(max(speed, 0.58), 1.72)

        rx, ry = repel[i]
        vx = math.cos(angle) * speed + rx
        vy = math.sin(angle) * speed + ry

        x = float(p["x"]) + vx
        y = float(p["y"]) + vy
        r = float(p["r"])

        if x < MARGIN + r:
            x = MARGIN + r
            angle = math.pi - angle + rng.uniform(-0.22, 0.22)
        elif x > WIDTH - MARGIN - r:
            x = WIDTH - MARGIN - r
            angle = math.pi - angle + rng.uniform(-0.22, 0.22)

        if y < MARGIN + r:
            y = MARGIN + r
            angle = -angle + rng.uniform(-0.22, 0.22)
        elif y > HEIGHT - MARGIN - r:
            y = HEIGHT - MARGIN - r
            angle = -angle + rng.uniform(-0.22, 0.22)

        p["x"] = x
        p["y"] = y
        p["angle"] = angle
        p["speed"] = speed
        p["vx"] = math.cos(angle) * speed
        p["vy"] = math.sin(angle) * speed


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
                alpha = int(82 * (1 - distance / CONNECT_DISTANCE))
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
    for frame in range(FRAMES):
        frames.append(draw_frame(particles))
        step(particles, frame)

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
