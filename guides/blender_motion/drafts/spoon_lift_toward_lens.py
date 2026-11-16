"""First spoonful toward the lens (catalog v3, 2026-11-16): bite_pip_dish_v2's static 45 degree food-only lift, with
the approved serving_bowl and dessert spoon in place of the pasta plate and fork. The cropped pinch grip is the fork
guide's: same CC0 pose, side, orientation and attachment relative to the utensil."""
import math

import bpy
from mathutils import Vector

from drafts.common import new_state, finish
from drafts.bowl_steam_overhead import serving_bowl, rim
from drafts.plates_v2 import FORK_PITCH, window

IDS = ('spoon_lift_toward_lens',)

SUPPORT = .785
IN = .0254
# Request: phone about 14 in from the bowl, seated at chest height.
LENS_DISTANCE = 14 * IN
ELEVATION = 40
# Spoon heading: dipped with its bowl toward the far left and the handle toward the diner's right hand (bottom right
# of frame); carried with the tip turned toward the lens (the mouth), as a spoon comes to the lips.
START_YAW, END_YAW = 60, 100
# Dipped steeper than the fork so the handle clears the tall bowl's rim; level when carrying the spoonful.
START_PITCH, END_PITCH = -40, 0
# Beats: the lift runs from 1.0 s to 3.5 s of the 5 s move, then holds.
LIFT = (.2, .7)
HOLD_FROM_LENS = 8 * IN
HOLD_SHIFT = (-.03, 0, .0)


def build(gid, record, P):
    if gid not in IDS:
        raise ValueError(gid)
    A, H = P.A, P.H
    state = new_state()
    A.table((.22, .18, 0), .70).location = (0, .40, 0)
    P.role(P.V.chair((0, 1.22, 0)), 'background')
    bowl = serving_bowl(P, (0, 0, SUPPORT), record.get('scanPrep'))
    meshes = P.members(bowl)
    # The spoonful is the subject at the target frame; at 14 in the whole bowl cannot fit the hero band with it.
    for obj in meshes:
        P.A.tag(obj, 'support', 'The approved serving_bowl the spoonful comes from')
    centre, rim_r, radius = rim(meshes)

    # The grip is fitted exactly as the fork guide fits it (utensil at FORK_PITCH, heading -X, palm down), then the
    # hand is parented to the spoon, so the hand-to-utensil pose is the approved one at every frame.
    spoon = A.spoon((0, 0, 0), role='hero')
    spoon.rotation_euler = (math.radians(FORK_PITCH), 0, math.pi / 2)
    bpy.context.view_layer.update()
    # Same 4 to 5 cm from the handle end as the fork grip; 2.5 mm higher for the spoon's thicker, raised handle.
    grip = spoon.matrix_world @ Vector((0, -.08, .0075))
    wrist = H.place('pinch', 'L', target=grip, forward=(-1, 0, 0), normal=(0, 0, -1), anchor='grip')
    P.role(wrist, 'hand'); wrist['p0_hand'] = True; wrist['p0_cropped_grip'] = True; P.attach(wrist, spoon)

    heading = Vector((-math.sin(math.radians(START_YAW)), math.cos(math.radians(START_YAW)), 0))
    # Spoon bowl centre (local y .034) 4.5 cm past the bowl centre toward the far left, 2 cm under the rim, so the
    # knuckles stay above the open bowl, clear of the rim.
    dip = Vector((centre.x, centre.y, centre.z - .020)) + heading * .045
    lens = centre + LENS_DISTANCE * Vector((0, -math.cos(math.radians(ELEVATION)), math.sin(math.radians(ELEVATION))))
    lens.z -= .03
    aim = Vector((centre.x, centre.y, centre.z - .03))
    # Held about 8 in from the lens (closest focus), a little left of the sight line so the grip stays in frame.
    hold = lens + (aim - lens).normalized() * HOLD_FROM_LENS + Vector(HOLD_SHIFT)

    def place(location_of_spoon_bowl, pitch_deg, yaw_deg):
        spoon.rotation_euler = (math.radians(pitch_deg), 0, math.radians(yaw_deg))
        bpy.context.view_layer.update()
        offset = spoon.matrix_world.to_3x3() @ Vector((0, .034, 0))
        spoon.location = location_of_spoon_bowl - offset

    def action(u):
        k = window(u, *LIFT)
        # The wrist carries the bowl up first, then toward the lens (an arc about a low elbow).
        up = window(u, LIFT[0], LIFT[0] + .8 * (LIFT[1] - LIFT[0]), .3)
        toward = k
        position = Vector((dip.x + (hold.x - dip.x) * toward, dip.y + (hold.y - dip.y) * toward,
                           dip.z + (hold.z - dip.z) * up))
        place(position, START_PITCH + (END_PITCH - START_PITCH) * k, START_YAW + (END_YAW - START_YAW) * k)
        spoon.keyframe_insert('location'); spoon.keyframe_insert('rotation_euler')
        bpy.context.view_layer.update()
    state['actions'].append(action)
    state['hand_count'] = 1

    source = Vector(state.get('light_position', (-.65, -.18, 1.5)))
    angle = math.atan2(source.y - centre.y, source.x - centre.x)
    P.light_edge('Bowl light-facing rim', [Vector((centre.x + rim_r * math.cos(a), centre.y + rim_r * math.sin(a), centre.z))
                                           for a in [angle + math.radians(-25 + j * 50 / 24) for j in range(25)]],
                 .0003, parent=meshes[0])

    state['spoon'] = spoon; state['hand'] = wrist; state['bowl_meshes'] = meshes
    state['dish'] = dict(rim_z=round(centre.z, 4), rim_radius=round(rim_r, 4), radius=round(radius, 4),
                         dip=[round(v, 4) for v in dip], hold=[round(v, 4) for v in hold],
                         hold_from_lens_in=round((hold - lens).length / IN, 2))
    state['contacts'].append(dict(kind='spoon_grip', hand=wrist.name, prop=spoon.name, grip=list(grip),
                                  grip_source='bite_pip_dish_v2 fork pinch (same pose, side, orientation, attachment)',
                                  crop='Only the small grip at the bottom right; palm, wrist and arm fade out'))
    state['adaptations'].append('Food only, phone static at about 40 degrees down, lens about 14 in from the bowl: the '
                                'spoon rests dipped in the bowl for 1 s, lifts up and toward the lens until 3.5 s, '
                                'levels out and holds about 8 in in front of the lens.')
    hero = [o for o in P.members(spoon) if o.get('composition_role') == 'hero']
    return finish(state, hero, lens, aim)
