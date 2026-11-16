"""Soft glass-like volumes from native surface orientation, without ink edges."""
import cv2
import numpy as np
from PIL import Image

GLASS_TINT = (74, 137, 160)
GLASS_HIGHLIGHT = (243, 252, 255)

def render(fields, mask, seconds, opacity=.65, solid_surfaces=False):
    data = np.asarray(fields.convert('RGB')).astype(np.float32) / 255
    data = np.where(data <= .04045, data / 12.92, ((data + .055) / 1.055) ** 2.4)
    data = cv2.GaussianBlur(data, (0, 0), 2.2)
    fresnel, light, height = data[:, :, 0], data[:, :, 1], data[:, :, 2] * 3
    role = mask[:, :, 1].astype(np.float32) / 255
    emphasis = np.interp(role, [0, .22, .65, 1], [0, .025, .34, 1]).astype(np.float32)
    coverage = mask[:, :, 3].astype(np.float32) / 255
    rim = np.clip(fresnel, 0, 1) ** .72
    # A broad world-space light sweep moves over the volumes; it does not
    # introduce scan-line grids, topology wires or texture noise.
    sweep = np.maximum(0, np.cos((height * .50 - seconds / 6) * 2 * np.pi)) ** 10
    shine = np.clip(.10 + .60 * light ** 3 + .55 * rim + .30 * sweep, 0, 1)
    tint = np.array(GLASS_TINT, np.float32)
    white = np.array(GLASS_HIGHLIGHT, np.float32)
    rgb = tint + (white - tint) * shine[:, :, None]
    # Only explicitly animated practical diffusers carry a blue-channel light
    # field. Old masks have B=0, so their approved material stays identical.
    warm = mask[:, :, 2].astype(np.float32) / 255
    warm_rgb = np.array([255, 207, 106],np.float32) + np.array([0, 38, 85],np.float32)*shine[:, :, None]
    rgb = rgb*(1-warm[:, :, None]) + warm_rgb*warm[:, :, None]
    # Preserve an explicitly marked, instruction-bearing icon. This is a small
    # semantic mask, not an edge or texture pass over the scene's geometry.
    semantic=np.clip((mask[:, :, 0].astype(np.float32)/255-.8)/.2,0,1)*(1-warm)
    rgb=rgb*(1-semantic[:, :, None])+tint*semantic[:, :, None]
    body = (.22 + .50 * rim + .08 * light + .14 * sweep) * emphasis * coverage
    aura = cv2.GaussianBlur(rim * emphasis * coverage, (0, 0), 5) * .14
    if solid_surfaces:
        # Surface visibility belongs to the image view. At 100%, the hero
        # objects are opaque; only context objects and the outside aura are
        # subdued. Fresnel still shapes the color, rather than hiding faces.
        strength = np.interp(role, [0, .08, .22, .65, 1], [0, 0, .55, .92, 1])
        body = strength * coverage
        aura *= 1 - np.clip(body, 0, 1)
    alpha = np.clip((body + aura) * opacity, 0, opacity)
    return Image.fromarray(np.dstack([np.rint(rgb).astype(np.uint8),
                                     np.rint(alpha * 255).astype(np.uint8)]))
