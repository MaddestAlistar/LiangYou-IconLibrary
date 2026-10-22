#!/usr/bin/env python3
"""Optimize seven reported-stuttering Motion Photo GIFs for icon-list renderers.

Only writes GIFs; preserves existing file paths, subscriptions, and older icons.
The original embedded 720px/24fps video is used, never a previously compressed GIF.
"""
from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "icons" / "liangyou"
STEMS = (
    "hemaxiansheng", "kfc", "mogu-ultra", "niubi",
    "sdx-life", "we-emby", "yunhai",
)

def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def main():
    with tempfile.TemporaryDirectory(prefix="liangyou-gif-") as tmp:
        temp = Path(tmp)
        for stem in STEMS:
            jpg = ICONS / (stem + "-01.jpg")
            gif = ICONS / (stem + "-animated-01.gif")
            original = jpg.read_bytes()
            marker = original.find(b"ftyp")
            start = marker - 4
            if original[:2] != b"\xff\xd8" or start < 2 or original[marker:marker+4] != b"ftyp":
                raise ValueError("Missing original embedded video: " + str(jpg))
            movie = temp / (stem + ".mp4")
            palette = temp / (stem + "-palette.png")
            output = temp / (stem + ".gif")
            movie.write_bytes(original[start:])
            info = json.loads(subprocess.check_output([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,avg_frame_rate,nb_frames",
                "-of", "json", str(movie)], text=True))["streams"][0]
            if (int(info["width"]), int(info["height"]), info["avg_frame_rate"]) != (720, 720, "24/1"):
                raise ValueError("Unexpected source video: " + stem)
            expected = int(info["nb_frames"])
            # Match established older GIFs: 320px, 12fps, 80/90ms frame delays.
            # Keep all 256 palette entries; avoid spatial dithering noise which changes static
            # pixels between frames and increases data/compositing load in icon-list views.
            filters = "fps=12,scale=320:-1:flags=lanczos"
            run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(movie),
                "-vf", filters + ",palettegen=max_colors=256:stats_mode=full", str(palette))
            run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(movie),
                "-i", str(palette), "-lavfi",
                filters + "[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle",
                "-loop", "0", str(output))
            stream = json.loads(subprocess.check_output([
                "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,nb_read_frames",
                "-of", "json", str(output)], text=True))["streams"][0]
            count = int(stream["nb_read_frames"])
            if ((int(stream["width"]), int(stream["height"])) != (320, 320)
                    or count < int(expected * 0.45) or count > expected or not output.read_bytes().startswith(b"GIF89a")
                    or output.stat().st_size < 200_000):
                raise ValueError("Unexpected output GIF: " + stem)
            output.replace(gif)
            print(f"Updated {stem}: source {expected} frames -> GIF {count} frames ({gif.stat().st_size} bytes)")
    print("Exactly seven GIF paths optimized; three unaffected motion GIFs untouched.")

if __name__ == "__main__":
    main()
