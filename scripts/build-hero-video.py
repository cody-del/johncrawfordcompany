#!/usr/bin/env python3
"""Install an approved hero edit and matching posters without re-cutting it.

Usage: python3 scripts/build-hero-video.py --approved-dir /path/to/approved-edit --ffmpeg /path/to/ffmpeg
The approved folder contains edit-manifest.json and the verified desktop/mobile MP4 exports.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--approved-dir', type=Path, required=True)
parser.add_argument('--ffmpeg', default='ffmpeg')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
assets = root / 'dist/assets'
manifest = json.loads((args.approved_dir / 'edit-manifest.json').read_text())
exports = {
    'desktop': ('john-crawford-new-hero-web.mp4', 'hero-shades-loop-desktop-20261104.mp4', [1280, 720]),
    'mobile': ('john-crawford-new-hero-mobile.mp4', 'hero-shades-loop-mobile-20261104.mp4', [540, 960])
}
replacements = {}
for layout, (source_name, filename, dimensions) in exports.items():
    source = args.approved_dir / source_name
    target = assets / filename
    shutil.copyfile(source, target)
    poster = f'hero-shades-poster-{layout}-20261104.webp'
    subprocess.run([args.ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(target),
                    '-frames:v', '1', '-c:v', 'libwebp', '-quality', '88', str(assets / poster)], check=True)
    replacements[f'hero-room-loop-{layout}.mp4'] = filename
    replacements[f'hero-room-poster-{layout}.webp'] = poster
    manifest[layout] = {'file': filename, 'size': dimensions,
                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'poster': poster}

# The shared hero appears on Home and the two ad landing pages. Preserve all
# copy, overlay styles, controls and motion preferences; replace media only.
for relative in ['index.html', 'lp/custom-window-treatments/index.html', 'lp/motorized-shades/index.html']:
    path = root / 'dist' / relative
    html = path.read_text()
    for old, new in replacements.items():
        html = html.replace(old, new)
    html = html.replace('alt="" width="1600" height="900" fetchpriority="high"',
                        'alt="" width="1280" height="720" fetchpriority="high"')
    path.write_text(html)

# Keep the retired media in Git history rather than in the deployed assets.
for old in replacements:
    (assets / old).unlink(missing_ok=True)
manifest.pop('website_status', None)
manifest['source'] = 'Client-supplied installs - 8 of 12.mov, installs - 9 of 12.mov and installs - 3 of 12.mov. No footage from the former hero.'
manifest['fallbacks'] = 'Matching posters; existing overlay, pause control, reduced-motion, data-saver and offscreen-pause behavior retained.'
(root / 'reference').mkdir(exist_ok=True)
(root / 'reference/hero-video-edit.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
print('Approved hero video and matching posters installed on Home and both shared landing-page heroes.')
