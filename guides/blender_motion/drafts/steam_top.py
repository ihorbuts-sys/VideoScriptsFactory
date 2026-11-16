"""Top-down steam draft (2026-11-11): the finished rosetta cup of pour_top_down_latte, phone flat above it, turning about
the vertical axis through the cup."""
import math

from mathutils import Matrix, Vector

from drafts.common import new_state, finish

IDS = ('steam_top_orbit',)

SUPPORT = .785
RIM = .128
LENS_ABOVE_RIM = .30
ARC_DEG = 40
# Camera 2.7 cm toward screen-down puts the cup centre 44% from the top (framing.md, RA2).
SCREEN_DOWN_OFFSET = .027
WITH_STEAM = False


def build(gid, record, P):
    if gid != 'steam_top_orbit':
        raise ValueError(gid)
    state = new_state()
    support = SUPPORT
    # Round table; its near edge 26 cm in front of the cup, so one arc of edge sits in the bottom of the frame.
    P.A.table((0, .34, 0), .60)
    drink, saucer = P.cup(0, 0, support, art='rosetta')
    for obj in P.members(drink):
        if 'hollow ceramic body' in obj.name:
            obj['p0_light_rim'] = True
    if WITH_STEAM:
        from drafts.steam_v2 import steam
        steam(P, state, support)
    # Window at about 1 o'clock behind the cup: side-back light on the rim (framing.md light cues).
    state['light_position'] = (.95, 1.30, support+.60)
    cup_centre = Vector((0, 0, 0))
    lens_z = support+RIM+LENS_ABOVE_RIM
    position = Vector((0, -SCREEN_DOWN_OFFSET, lens_z))
    target = Vector((0, -SCREEN_DOWN_OFFSET, support+.10))
    state['camera_up'] = (0., 1., 0.)

    def sample(u, p, t):
        angle = math.radians(ARC_DEG*(1-P.smooth(u)))
        turn = Matrix.Rotation(angle, 3, 'Z')
        offset = Vector((p.x-cup_centre.x, p.y-cup_centre.y, 0))
        pos = Vector((cup_centre.x, cup_centre.y, p.z))+turn@offset
        state['camera_up'] = tuple(turn@Vector((0, 1, 0)))
        return pos, pos-Vector((0, 0, p.z-t.z))

    state['contacts'].append(dict(kind='flat_top_down_turn', lens_above_rim=LENS_ABOVE_RIM, arc_deg=ARC_DEG,
                                  axis='vertical through the cup centre', pitch_deg=90, support_surface_z=support))
    state['adaptations'].append(f'Phone flat, lens {LENS_ABOVE_RIM*100:.0f} cm above the rim, looking straight down; it turns '
                                f'{ARC_DEG} degrees clockwise (seen from above) about the vertical axis through the cup, no rise or tilt. '
                                'The handle goes from about 4 o\'clock to 3 o\'clock in the frame.')
    state['adaptations'].append('Steam strands ' + ('kept' if WITH_STEAM else 'left out: seen from straight above they project onto the latte art and do not read as rising steam') + '.')
    return finish(state, P.members(drink), position, target, sample)
