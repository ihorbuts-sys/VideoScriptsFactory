#!/usr/bin/env python3
"""Stacks strip PNGs into review sheets of N rows each: python sheets.py <strip dir> <out dir> [rows]"""
import glob, os, sys
from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
rows = int(sys.argv[3]) if len(sys.argv) > 3 else 8
os.makedirs(out, exist_ok=True)
strips = sorted(glob.glob(os.path.join(src, "*_strip.png")))
for k in range(0, len(strips), rows):
    batch = strips[k:k + rows]
    ims = [Image.open(p) for p in batch]
    w = max(i.width for i in ims)
    h = sum(i.height + 22 for i in ims)
    sheet = Image.new("RGB", (w, h), (12, 12, 14))
    d = ImageDraw.Draw(sheet)
    y = 0
    for p, im in zip(batch, ims):
        d.text((6, y + 4), os.path.basename(p)[:-10], fill=(255, 210, 74))
        sheet.paste(im, (0, y + 22))
        y += im.height + 22
    sheet.save(os.path.join(out, f"sheet_{k // rows + 1:02d}.png"))
print(len(strips), "strips in", (len(strips) + rows - 1) // rows, "sheets")
