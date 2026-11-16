"""Uploads, downloads and checks the content media listed in media_manifest.json against the Drive folder
VideoScriptsFactor-media through rclone. Run it through scripts/tools/sync_media.sh.

Every remote call is scoped with --drive-root-folder-id to the folder id in the manifest, so nothing is written outside
that folder. Upload makes the animated WebP (Android) from each animated PNG first and records it in the manifest.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "media_manifest.json"
CACHE = ROOT / ".media_cache"
REMOTE = os.environ.get("MEDIA_REMOTE", "gdrive") + ":"
UPLOAD = ("animation:published", "animation:approved-draft", "model")
OPTIONAL = ("optional:object-approval-renders",)
WEBP_QUALITY = 72


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load():
    return json.loads(MANIFEST.read_text())


def save(manifest):
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")


def local(entry):
    return (ROOT / entry["path"]).resolve()


def rclone(manifest, *args, capture=False):
    cmd = ["rclone", *args, "--drive-root-folder-id", manifest["driveFolderId"]]
    print("+", " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd, check=True, text=True, capture_output=capture)


def chosen(manifest, include_optional):
    cats = UPLOAD + (OPTIONAL if include_optional else ())
    return [e for e in manifest["files"] if e["category"] in cats or e["category"].startswith("animation-webp:")
            and e["category"].split(":", 1)[1] in cats]


def make_webp(manifest):
    """Animated WebP for every animated PNG that will be uploaded; recorded as its own manifest entry."""
    from PIL import Image  # pip install Pillow
    known = {e["drivePath"]: e for e in manifest["files"]}
    made = 0
    for e in list(manifest["files"]):
        if e["category"] not in UPLOAD or "webpDrivePath" not in e:
            continue
        src, dst = local(e), CACHE / "webp" / Path(e["webpDrivePath"]).name
        old = known.get(e["webpDrivePath"])
        if old and dst.is_file() and old.get("sourceSha256") == e["sha256"] and sha256(dst) == old["sha256"]:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(src)
        frames, durations = [], []
        for i in range(getattr(im, "n_frames", 1)):
            im.seek(i)
            frames.append(im.convert("RGBA").copy())
            durations.append(int(round(im.info.get("duration", 66.67))))
        frames[0].save(dst, save_all=True, append_images=frames[1:], duration=durations, loop=0,
                       quality=WEBP_QUALITY, method=4, lossless=False)
        entry = {"path": str(dst.relative_to(ROOT)), "bytes": dst.stat().st_size, "sha256": sha256(dst),
                 "category": "animation-webp:" + e["category"], "location": "drive",
                 "drivePath": e["webpDrivePath"], "guideId": e.get("guideId"), "sourceSha256": e["sha256"]}
        if old:
            old.update(entry)
        else:
            manifest["files"].append(entry)
            known[entry["drivePath"]] = entry
        made += 1
    return made


def stage(entries, extra=()):
    """A temporary tree of symlinks laid out like the Drive folder."""
    tmp = Path(tempfile.mkdtemp(prefix="media_stage_"))
    for e in entries:
        src = local(e)
        if not src.is_file():
            sys.exit(f"missing local file: {e['path']}")
        if sha256(src) != e["sha256"]:
            sys.exit(f"checksum differs from the manifest: {e['path']}")
        link = tmp / e["drivePath"]
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(src)
    for src, rel in extra:
        link = tmp / rel
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(src)
    return tmp


def upload(args):
    manifest = load()
    if not args.dry_run:
        print(f"webp made: {make_webp(manifest)}")
        for e in manifest["files"]:
            if e["category"] in UPLOAD + OPTIONAL or e["category"].startswith("animation-webp:"):
                e["location"] = "drive"
        save(manifest)
    entries = chosen(manifest, args.include_optional)
    tree = stage(entries, extra=[(MANIFEST, "media_manifest.json")])
    try:
        flags = ["--copy-links", "--checksum", "--transfers", "4"] + (["--dry-run"] if args.dry_run else [])
        rclone(manifest, "copy", str(tree), REMOTE, *flags)
        if not args.dry_run:
            rclone(manifest, "check", str(tree), REMOTE, "--copy-links", "--one-way")
    finally:
        shutil.rmtree(tree)
    total = sum(e["bytes"] for e in entries)
    print(f"{'would upload' if args.dry_run else 'uploaded and verified'}: {len(entries)} files, {total / 1e9:.3f} GB")


def download(args):
    manifest = load()
    dest = Path(args.dest).resolve() if args.dest else ROOT
    tmp = Path(tempfile.mkdtemp(prefix="media_pull_"))
    try:
        rclone(manifest, "copy", REMOTE, str(tmp), "--checksum", "--transfers", "4")
        placed, bad = 0, []
        for e in manifest["files"]:
            got = tmp / e["drivePath"]
            if not got.is_file():
                continue
            rel = e["path"]
            if rel.startswith("../"):
                rel = "media/" + e["drivePath"]
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(got, out)
            (bad.append(rel) if sha256(out) != e["sha256"] else None)
            placed += 1
        print(f"downloaded {placed} files into {dest}; checksum mismatches: {len(bad)}")
        for rel in bad:
            print("  mismatch:", rel)
    finally:
        shutil.rmtree(tmp)


def status(args):
    manifest = load()
    out = rclone(manifest, "lsjson", REMOTE, "-R", "--files-only", "--hash", capture=True).stdout
    remote = {f["Path"]: f for f in json.loads(out or "[]")}
    want = {e["drivePath"]: e for e in chosen(manifest, True)}
    want["media_manifest.json"] = None
    missing = sorted(p for p in want if p not in remote)
    extra = sorted(p for p in remote if p not in want and not p.startswith("music/"))
    print(f"remote files: {len(remote)}; expected (incl. optional): {len(want)}")
    print(f"missing on Drive: {len(missing)}")
    for p in missing[:50]:
        print("  -", p)
    print(f"on Drive but not in the manifest: {len(extra)}")
    for p in extra[:50]:
        print("  +", p)
    music = [e for e in manifest["files"] if e["category"] == "music"]
    have = sum(1 for e in music if e["drivePath"] in remote)
    print(f"music in music/: {have} of {len(music)} (the rest is in the parent folder until moved)")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    up = sub.add_parser("upload")
    up.add_argument("--include-optional", action="store_true")
    up.add_argument("--dry-run", action="store_true")
    down = sub.add_parser("download")
    down.add_argument("--dest")
    sub.add_parser("status")
    args = parser.parse_args()
    {"upload": upload, "download": download, "status": status}[args.cmd](args)


if __name__ == "__main__":
    main()
