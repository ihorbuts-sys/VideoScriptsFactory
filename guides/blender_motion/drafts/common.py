"""What p0_scenes.build's local finish() does, for draft modules."""
from mathutils import Vector


def new_state():
    return dict(hero=[], actions=[], contacts=[], adaptations=[], camera_height_support=0., hand_count=0, silhouettes=0)


def finish(state, hero, position, target, sample=None):
    state['hero'] = hero
    state['target_position'] = Vector(position)
    state['target_aim'] = Vector(target)
    state['sample'] = sample or (lambda u, p, t: (p, t))
    return state
