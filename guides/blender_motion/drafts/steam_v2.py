"""Steam and cup-only sip drafts (2026-11-10 audit): static phone, cup on its saucer, side-back window cue."""
import json
import math

import bpy
from mathutils import Vector

from drafts.common import new_state, finish

IDS = ('steam_low_backlit_v2', 'steam_static_low', 'sip_cup_only')

SUPPORT = .785


def steam(P, state, support):
    """The published steam strands (p0_scenes steam branch): same points, radius and drift. Role drink_contents, so the
    strands rise into the free band above the cup instead of counting in the hero band."""
    curls = []
    for side in [-1, 1]:
        points = [(side*.012+.007*math.sin(k*.8), 0, support+.13+k*.016) for k in range(9)]
        strand = P.A.tag(P.G.tube('Steam strand', points, .00075), 'drink_contents',
                         'Steam stays attached above the coffee and rises into the free band above the cup')
        strand['p0_steam_points'] = json.dumps(points)
        curls.append(strand)

    def action(u):
        for k, obj in enumerate(curls):
            obj.location.x = .003*math.sin(u*math.tau+k)
            obj.keyframe_insert('location')
    state['actions'].append(action)
    return curls


def aimed(target, distance, pitch, azimuth):
    """Lens position `distance` from `target`, `pitch` degrees down, `azimuth` degrees right of the -Y customer side."""
    p, a = math.radians(pitch), math.radians(azimuth)
    return Vector(target)+Vector((distance*math.cos(p)*math.sin(a), -distance*math.cos(p)*math.cos(a), distance*math.sin(p)))


def build(gid, record, P):
    state = new_state()
    support = SUPPORT
    if gid == 'steam_low_backlit_v2':
        # The cup sits 26 cm in from the near table edge; the lens at 30 cm is past the edge (portrait edge hold).
        P.A.table((0, .39, 0), .65)
        drink, saucer = P.cup(0, 0, support)
        steam(P, state, support)
        window = P.V.window((.95, 1.30, support+.60))
        P.role(window, 'background')
        state['light_position'] = (.95, 1.30, support+.60)
        target = Vector((0, 0, support+.060))
        state['contacts'].append(dict(kind='static_edge_hold', lens_above_table=.075, table_edge_from_cup=.26, support_surface_z=support))
        state['adaptations'].append('Static phone held just past the near table edge at cup height, 30 cm from the cup; the window is behind and to the right, the area behind the steam stays empty for a dark wall.')
        return finish(state, P.members(drink), aimed(target, .34, 2.5, 8), target)
    if gid == 'steam_static_low':
        P.A.table((.10, .30, 0), .65)
        drink, saucer = P.cup(0, 0, support)
        steam(P, state, support)
        window = P.V.window((-1.15, 1.20, support+.60))
        P.role(window, 'background')
        state['light_position'] = (-1.15, 1.20, support+.60)
        target = Vector((0, 0, support+.060))
        state['contacts'].append(dict(kind='static_table_brace', pitch_down_deg=15, support_surface_z=support))
        state['adaptations'].append('Static phone braced on the table, 15 degrees down, 30 cm from the cup; window light behind and to the left, empty dark band above the cup for the steam.')
        return finish(state, P.members(drink), aimed(target, .33, 15, 10), target)
    if gid == 'sip_cup_only':
        P.A.table((.10, .30, 0), .65)
        drink, saucer = P.cup(0, 0, support)
        P.role(saucer, 'hero')
        window = P.V.window((-.75, 1.30, support+.60))
        P.role(window, 'background')
        state['light_position'] = (-.75, 1.30, support+.60)
        # Handle turned to the right-front, toward the drinker's right hand.
        heading = math.radians(-40)
        drink.rotation_euler.z = heading
        bpy.context.view_layer.update()
        radial = Vector((math.cos(heading), math.sin(heading), 0))
        forward = -radial
        palm = Vector((0, 0, 1)).cross(forward)
        grip = Vector((0, 0, support+.010+.088))+radial*.078
        hand = P.hand(tuple(grip), forward=tuple(forward), normal=tuple(palm), side='R', pose='pinch')
        hand['p0_cropped_grip'] = True
        P.attach(hand, drink)
        state['hand_count'] = 1
        start = drink.location.copy()

        def action(u):
            lift = P.smooth((u-.15)/.60)
            drink.location = start+Vector((.20*lift, -.12*lift, .38*lift))
            drink.keyframe_insert('location')
        state['actions'].append(action)
        state['contacts'].append(dict(kind='cup_lift_out', hand=hand.name, saucer=saucer.name, saucer_stays=True, support_surface_z=support))
        state['adaptations'].append('Phone static at 45 degrees, 30 cm from the cup; one hand lifts the cup by its handle up and toward the drinker until it leaves the top of the frame; the saucer stays and is the target.')
        target = Vector((0, 0, support+.012))
        return finish(state, P.members(saucer), aimed(target, .30, 45, 10), target)
    raise ValueError(gid)
