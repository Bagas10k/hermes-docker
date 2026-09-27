"""Bounded local screenshot palette extraction; no semantic/OCR claims."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import warnings
from PIL import Image, ImageOps


def luminance(rgb):
    c = [v / 255 for v in rgb]
    c = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in c]
    return sum(a * b for a, b in zip(c, (.2126, .7152, .0722)))


def contrast(a, b):
    x, y = sorted((luminance(a), luminance(b)))
    return (y + .05) / (x + .05)


def extract(path, crop=None, colors=8, matte='#FFFFFF'):
    path = Path(path)
    if path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('Input exceeds 32 MiB')
    if not 2 <= colors <= 16:
        raise ValueError('colors must be 2..16')
    warnings.simplefilter('error', Image.DecompressionBombWarning)
    with Image.open(path) as source:
        if source.width * source.height > 40_000_000:
            raise ValueError('Input exceeds 40 megapixels')
        if source.format not in ('PNG', 'JPEG', 'WEBP') or getattr(source, 'n_frames', 1) != 1:
            raise ValueError('Use single-frame PNG, JPEG, or WebP')
        image = ImageOps.exif_transpose(source)
        size = image.size
        if crop:
            x1, y1, x2, y2 = crop
            if not (0 <= x1 < x2 <= size[0] and 0 <= y1 < y2 <= size[1]):
                raise ValueError('crop outside oriented image bounds')
            image = image.crop(crop)
        image.thumbnail((384, 384), Image.Resampling.LANCZOS)
        rgba = image.convert('RGBA')
        base = Image.new('RGBA', rgba.size, matte)
        image = Image.alpha_composite(base, rgba).convert('RGB')
        quantized = image.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        palette = quantized.getpalette()
        entries = []
        for count, index in sorted(quantized.getcolors(), reverse=True):
            rgb = tuple(palette[index * 3:index * 3 + 3])
            black, white = contrast(rgb, (0, 0, 0)), contrast(rgb, (255, 255, 255))
            entries.append({'hex': '#%02X%02X%02X' % rgb, 'sample_fraction': count / (image.width * image.height), 'on_color': '#000000' if black >= white else '#FFFFFF', 'contrast_black': black, 'contrast_white': white, 'normal_text_pass': max(black, white) >= 4.5})
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'schema_version': 1, 'source': str(path.resolve()), 'sha256': digest, 'oriented_size': size, 'crop': crop, 'sample_size': image.size, 'matte': matte, 'assumption': 'sRGB; embedded color profiles not converted', 'semantic_roles': 'unassigned: human or vision review required', 'palette': entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image')
    parser.add_argument('--crop', type=int, nargs=4)
    parser.add_argument('--colors', type=int, default=8)
    parser.add_argument('--matte', default='#FFFFFF')
    args = parser.parse_args()
    try:
        print(json.dumps(extract(args.image, args.crop, args.colors, args.matte), indent=2))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
