#!/usr/bin/env python3
"""Rebuild the 10 October 22 motion GIFs from MP4 clips embedded in their source JPGs."""
from pathlib import Path
import subprocess
import tempfile
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "icons" / "liangyou"
STEMS = (
    "chenyu", "hemaxiansheng", "kfc", "mogu-ultra", "niubi",
    "sdx-life", "we-emby", "yunhai", "zhenying", "zhezhimao",
)

def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

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
                "-vf", "fps=25,scale=320:-1:flags=lanczos,palettegen=stats_mode=full:max_colors=256", str(palette))
            run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(movie), "-i", str(palette),
                "-lavfi", "fps=25,scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle",
                "-loop", "0", str(gif))
            if not gif.read_bytes().startswith(b"GIF89a") or gif.stat().st_size < 200000:
                raise ValueError(f"Unexpected optimized GIF: {gif}")
            webp = ICONS / f"{stem}-animated-01.webp"
            run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(movie),
                "-vf", "fps=24,scale=480:-1:flags=lanczos", "-c:v", "libwebp_anim",
                "-q:v", "95", "-loop", "0", "-an", str(webp))
            ffprobe = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=nb_frames,width,height,avg_frame_rate", "-of", "json", str(movie)])
            meta = json.loads(ffprobe)["streams"][0]
            if (meta["width"], meta["height"], meta["avg_frame_rate"]) != (720, 720, "24/1"):
                raise ValueError(f"Source video unexpectedly changed: {stem}")
            expected = int(meta["nb_frames"])
            raw_webp = webp.read_bytes()
            if raw_webp[:4] != b"RIFF" or raw_webp[8:12] != b"WEBP":
                raise ValueError(f"Invalid animated WebP file: {stem}")
            pos, frames = 12, 0
            while pos + 8 <= len(raw_webp):
                tag = raw_webp[pos:pos + 4]
                size = struct.unpack_from("<I", raw_webp, pos + 4)[0]
                if tag == b"ANMF":
                    frames += 1
                pos += 8 + size + (size % 2)
            if pos != len(raw_webp) or frames != expected:
                raise ValueError(f"WebP dropped frames: {stem} ({frames} != {expected})")
            if webp.stat().st_size < 200000:
                raise ValueError(f"Unexpected tiny WebP: {stem}")
            print(f"Quality rebuild {stem}: GIF {gif.stat().st_size} bytes, WebP {webp.stat().st_size} bytes, {frames}/{expected} video frames")


    # Independent HD subscription; keep the existing GIF subscriptions unchanged.
    display = {
        "chenyu": "宸宇", "hemaxiansheng": "盒马鲜生", "kfc": "KFC",
        "mogu-ultra": "蘑菇Ultra", "niubi": "牛逼", "sdx-life": "SDX Life",
        "we-emby": "WE Emby", "yunhai": "云海", "zhenying": "臻影", "zhezhimao": "这只猫"
    }
    base = "https://raw.githubusercontent.com/MaddestAlistar/LiangYou-IconLibrary/main/icons/liangyou/"
    index = {
        "name": "良友高清动态图标库",
        "description": "良哥看未来｜高画质动态WebP｜适用于支持动画WebP的播放器｜更新时间：2026年10月22日",
        "icons": [
            {"name": display[stem] + " 高清动态", "url": base + stem + "-animated-01.webp"}
            for stem in STEMS
        ],
    }
    (ROOT / "LiangYou-HD-Animated-Icons.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
