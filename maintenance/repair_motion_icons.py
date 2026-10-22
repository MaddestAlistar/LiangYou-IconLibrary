#!/usr/bin/env python3
"""Rebuild the 10 October 22 motion GIFs from MP4 clips embedded in their source JPGs."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "icons" / "liangyou"
STEMS = (
    "chenyu", "hemaxiansheng", "kfc", "mogu-ultra", "niubi",
    "sdx-life", "we-emby", "yunhai", "zhenying", "zhezhimao",
)

def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    with tempfile.TemporaryDirectory(prefix="liangyou-motion-") as tmp:
        temp = Path(tmp)
        for stem in STEMS:
            jpg = ICONS / f"{stem}-01.jpg"
            gif = ICONS / f"{stem}-animated-01.gif"
            source = jpg.read_bytes()
            marker = source.find(b"ftyp")
            start = marker - 4
            if not source.startswith(bytes((255, 216))) or start < 2:
                raise ValueError(f"Missing original MP4 in {jpg}")
            movie = temp / f"{stem}.mp4"
            palette = temp / f"{stem}-palette.png"
            movie.write_bytes(source[start:])
            run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(movie),
                "-vf", "fps=15,scale=240:-1:flags=lanczos,palettegen=stats_mode=full:max_colors=256", str(palette))
            run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(movie), "-i", str(palette),
                "-lavfi", "fps=15,scale=240:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle",
                "-loop", "0", str(gif))
            if not gif.read_bytes().startswith(b"GIF89a") or gif.stat().st_size < 200000:
                raise ValueError(f"Unexpected optimized GIF: {gif}")
            print(f"Rebuilt {gif.relative_to(ROOT)} ({gif.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
