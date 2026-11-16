"""Texture-independent silhouettes plus a few large, denoised feature lines."""
import cv2
import numpy as np
from PIL import Image


def render(color, mask):
    rgb = np.asarray(color.convert('RGB'))
    height, width = rgb.shape[:2]
    # Work at guide-display scale so mesh facets, grain and tiny texture marks
    # cannot turn into hundreds of animated contour fragments.
    size = (width // 2, height // 2)
    small = cv2.resize(rgb, size, interpolation=cv2.INTER_AREA)
    small = cv2.medianBlur(small, 3)
    for _ in range(2):
        small = cv2.bilateralFilter(small, 9, 45, 6)
    smooth = cv2.resize(small, (width, height), interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
    features = cv2.Canny(cv2.GaussianBlur(gray, (3, 3), .8), 45, 110)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(features, 8)
    keep = np.zeros(count, np.uint8)
    for index in range(1, count):
        area = stats[index, cv2.CC_STAT_AREA]
        span = max(stats[index, cv2.CC_STAT_WIDTH], stats[index, cv2.CC_STAT_HEIGHT])
        if area >= 18 and span >= 10:
            keep[index] = 255
    features = cv2.resize(keep[labels], (width, height), interpolation=cv2.INTER_LINEAR)
    # The flat role pass preserves small essential silhouettes, including both
    # espresso streams, even when their color contrast is weak.
    role = cv2.medianBlur(mask[:, :, 1], 3)
    silhouette = cv2.Canny(cv2.GaussianBlur(role, (3, 3), .6), 35, 80)
    silhouette = cv2.dilate(silhouette, np.ones((2, 2), np.uint8))
    coverage = mask[:, :, 3].astype(np.float32) / 255
    emphasis = cv2.GaussianBlur(role, (3, 3), .7).astype(np.float32)
    feature_alpha = features.astype(np.float32) / 255 * emphasis * .55
    outer_alpha = silhouette.astype(np.float32) / 255 * emphasis
    alpha = np.maximum(feature_alpha, outer_alpha) * coverage
    fill_alpha = mask[:, :, 0].astype(np.float32) * coverage
    fill = Image.fromarray(np.dstack([smooth, np.rint(fill_alpha).astype(np.uint8)]))
    lines = np.zeros((height, width, 4), np.uint8)
    lines[:, :, :3] = (113, 153, 178)
    lines[:, :, 3] = np.rint(alpha).astype(np.uint8)
    ghost = Image.alpha_composite(fill, Image.fromarray(lines))
    ghost.putalpha(ghost.getchannel('A').point(lambda value: round(value * .65)))
    return ghost
