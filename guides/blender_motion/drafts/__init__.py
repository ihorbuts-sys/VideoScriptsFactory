"""Draft guide scenes, one module per family (steam_v2.py, plates_v2.py, ...), so parallel guide authors never edit the
same file. A module exposes IDS (the draft guide ids it builds) and build(gid, record, P), where P is p0_scenes. A
draft id moves into p0_scenes (or stays here) only when guide-publish promotes it."""
import importlib
import pkgutil


def build(gid, record, P):
    for info in pkgutil.iter_modules(__path__):
        if info.name.startswith('_') or info.name == 'common':
            continue
        module = importlib.import_module(f'{__name__}.{info.name}')
        if gid in getattr(module, 'IDS', ()):
            return module.build(gid, record, P)
    return None
