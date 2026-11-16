"""Seated canonical creator at a table place setting (owner-approved seated pose, 2026-11-10).

Same rig, skinning and mouth line as p0_people; only the skeleton is posed (hips on the seat, knees under the table,
hands on the table). No new geometry, no facial animation. Stage 1 pose probes (pose_seated_*) and the stage 2 people
guides: the cup and fork grips and the open-palm verdict are p0_people's approved poses, re-based on the seated head.
"""
import math
import bmesh
import bpy
import numpy as np
from mathutils import Vector, Quaternion, Matrix
from mathutils.bvhtree import BVHTree
import p0_people as PP
from prepare_rigged_characters import named
from coffee_scene_details import orient_bone
from build_creator_guides import ArmPose

TABLE_Z = .785                      # table top (A.table)
SEAT_Z = .48                        # dining chair seat top (V.chair)
HIP_JOINT_ABOVE_SEAT = .105         # hip joint centre over the seat; soft tissue under it compresses about 2 cm (judgement)
HIPS_Y = .07                        # pelvis over the chair, a little in front of its centre
LEAN = {'Hips': 6., 'Spine': 5., 'Spine1': 5., 'Spine2': 4.}   # forward lean toward the table, deg (judgement)
TABLE_RADIUS = .62                  # four-top round table (owner kept it): friend 1.3 m and propped phone 1.2 m stay over it
TABLE_EDGE_Y = -.22                 # her near table edge; she faces -Y
EYE_REST = Vector((0., -.145, 1.483))   # mid eye line of the source eye marks, rest pose
FACE_TOP_REST = 1.505               # protected face = eye line to chin (brows and hair may enter the upper band)
FRONT_LENS, REAR_LENS = 23, 24      # front camera (owner), rear 1x (about 45 deg horizontal in portrait, framing.md)
EYE_FROM_TOP = 1 / 3                # framing.md, RB15; owner: the eye line wins over the 5-10 deg pitch
FADE_FLOOR = TABLE_Z - .20          # character strokes fade in over 22 cm above this, so hands on the table stay drawn
CUP_SCALE, CUP_FACE_GAP = PP.CUP_SCALE, PP.CUP_FACE_GAP

# camera: (kind, lens-to-eye m, lens above the eyes m, deg to her right (+) or left (-)); look: share of the head turn;
# low_elbow: the bite keeps the elbow low beside her ribs and leans the trunk a little toward the fork (eating_arm_kinematics.md)
GUIDES = {
    'pose_seated_selfie': dict(act=None, camera=('hand', .60, 0., 5.), look=1.),
    'pose_seated_friend': dict(act=None, camera=('hand', 1.30, 0., 8.), look=1.),
    'pose_seated_propped': dict(act=None, camera=('propped', 1.20, None, 0.), look=1.),
    'bite_selfie_eye_v2': dict(act='bite', camera=('hand', .60, 0., 5.), look=1., low_elbow=True, grip='tripod'),
    'sip_selfie_eye_v2': dict(act='sip', camera=('hand', .60, 0., 5.), look=1.),
    'sip_high_lean_v2': dict(act='sip', camera=('hand', .60, .07, 5.), look=1.),
    'verdict_eye_level_v2': dict(act='gesture', camera=('hand', .60, 0., 5.), look=1.),
    'verdict_high_plate_v2': dict(act='plate', camera=('hand', .60, .07, 5.), look=1.),
    'bite_friend_three_quarter_v2': dict(act='bite', camera=('hand', .85, 0., -30.), look=.5, low_elbow=True),
    'sip_friend_side_v2': dict(act='sip', camera=('hand', .85, 0., -40.), look=.45),
    'verdict_friend_eye_v2': dict(act='gesture', camera=('hand', 1.30, 0., 8.), look=1.),
    'verdict_propped_rear': dict(act='gesture', camera=('propped', 1.20, None, 0.), look=1.),
}
IDS = tuple(GUIDES)

CUP_AT = Vector((.11, TABLE_EDGE_Y - .16, TABLE_Z))       # sip: saucer at her left front, in reach of the left hand
PLATE_AT = Vector((0, TABLE_EDGE_Y - .24, TABLE_Z))       # bite: plate in front of her
SETTING_PLATE_AT = Vector((0, TABLE_EDGE_Y - .36, TABLE_Z))
GESTURE_FROM_EYE = Vector((.20, -.08, -.26))              # open palm beside her chest (standing guide: 36 cm below the eyes)
PLATE_SCALE = .6                                          # owner: the dinner plate and pasta scaled 0.6 (a small plate and portion)
PLATE_BAND = (.30, .655)                                  # held plate rows from the top: inside the hero band, never past 66%
# The approved angles turned 12 deg about the fork's face, so the handle end clears the palm with the mid-handle grip.
FORK_OVER_PLATE = Vector((-.105, -.809, -.538))           # tines toward the food, start of the bite (judgement)
FORK_AT_MOUTH = Vector((-.799, .223, .555))                # rises toward the lips, the tine axis on the lips
HAND_AT_MOUTH = Vector((-.68, -.312, .663))              # knuckles toward the lips; wrist bend stays under 45 deg
FORK_TIP = Vector((0, .062, .010))                        # tine tips in A.fork's frame
FORK_GRIP = Vector((0, -.071, 0))                         # owner: held at the middle of the handle (-.1375 end to -.005 neck), 133 mm from the tine tips
BITE_POLE = Vector((.3, .25, -.9))                        # elbow down and a little out and back: upper arm near the ribs (ER1, ER2)
BITE_WRIST_BEND = 40.                                     # the wrist takes up the rest of the hand angle, under the 45 deg limit
BITE_LEAN = 3.                                            # trunk leans this much more toward the fork at the lips, head kept upright (ER3, ER2)
FORK_FACE_GAP = CUP_FACE_GAP                              # the forkful stops this far from the face, aimed at the lips
# grip='tripod': pencil hold, tines up (fork_grip.md FG1-FG4). Directions in the hand frame (forward, radial, palm).
TRIPOD_AXIS = Vector((.57, -.50, .62))                    # handle toward the tines: from the thumb web out past the fingertips (FG3, judgement)
TRIPOD_TOP = Vector((0, .8, -.6))                         # inside face up toward the index pad (dorsal-radial), its back on the middle finger (FG2, FG4)
TRIPOD_HAND_OVER_PLATE = (Vector((-.20, -.90, 0)), Vector((-.4, 0, 1)))   # hand forward and radial over the plate: the grip then
                                                          # points the tines down and in toward the plate centre (judgement)
TRIPOD_START_SHIFT = Vector((-.05, 0, 0))                 # the loaded tines wait over the plate centre, so the hand above them stays in frame
TRIPOD_ROLL = -40.                                        # the hand turned about the handle so it is tines-up at the lips (judgement)
TRIPOD_INDEX_UP = .38                                     # radial axis rise: index knuckle at least 2.5 cm over the little finger's
TRIPOD_SUPPORT_Y = -.066                                  # the middle finger's distal phalanx under the handle, just ahead of the pinch (FG2, FG5)
TRIPOD_FLEX = {'Middle': (1., 1.25, .40), 'Index': (1., .90, .35), 'Ring': (1., 1.30, .60), 'Pinky': (1., 1.30, .60)}   # joint share per finger
TRIPOD_CURL = {'Middle': 40., 'Ring': 48., 'Pinky': 52.}  # MCP flexion: middle support; ring and little curled under it (FG3, FG6)
CONTACT_GAP = .0005                                       # finger skin settles this far off the metal
FORK_SIDE = [(-.128, .0095), (-.112, .0105), (-.06, .0085), (-.005, .0040), (.008, .0045), (.022, .0105), (.030, .0110), (.062, .0110)]


def fork_clearance(local):
    """Signed distance (m, negative inside) from fork-local points to A.fork's stamped body, the head taken as solid."""
    x, y, z = local[:, 0], local[:, 1], local[:, 2]
    ys, ws = zip(*FORK_SIDE)
    half = np.where(y < -.128, np.sqrt(np.maximum(.0095 ** 2 - (y + .128) ** 2, 0)), np.interp(y, ys, ws))
    lift = .010 * np.maximum(0, (y - .015) / .047) ** 2 + .006 * np.maximum(0, (-.07 - y) / .058) ** 2
    d = np.stack([np.abs(x) - half, np.abs(z - lift) - .0011, np.maximum(-.1375 - y, y - .062)], axis=1)
    return np.linalg.norm(np.maximum(d, 0), axis=1) + np.minimum(d.max(axis=1), 0)
PLATE_TILTS = (25., 22., 28., 20., 30.)                   # top turned toward the lens, deg (owner 20-30); first that fits wins
PLATE_UNDER = [(r * PLATE_SCALE, z * PLATE_SCALE) for r, z in [(0, 0), (.09, 0), (.13, .012), (.15, .022), (.151, .029)]]
PLATE_TOP = [(r * PLATE_SCALE, z * PLATE_SCALE) for r, z in [(0, .009), (.09, .009), (.115, .015), (.139, .030), (.151, .029)]]
RIM_R = .151 * PLATE_SCALE
FINGER_R, THUMB_R = -.065, .074                            # waiter grip: the rim sits in the thumb web, fingertips reach just past the centre underneath, thumb pad on the rim top
GRIP_SIDE = -35.                                           # grip on the outer rim turned this far toward the lens, so the back of the hand faces it
PLATE_POLE = Vector((1., .2, -.3))                       # elbow out to her side, so the forearm runs level into the grip
PLATE_TURN = 12.                                          # she turns the dish in her hand to show it, deg (judgement)


def trim_face_mask(face):
    """Keep the measured face from the chin up to the eye line; drop the brow and hair part of the safety mask."""
    skin_mask = next(o for o in face if not o.get('p0_face_feature'))
    for obj in face:
        if obj is not skin_mask:
            bpy.data.objects.remove(obj, do_unlink=True)
    mesh = bmesh.new()
    mesh.from_mesh(skin_mask.data)
    bmesh.ops.delete(mesh, geom=[v for v in mesh.verts if (skin_mask.matrix_world @ v.co).z > FACE_TOP_REST], context='VERTS')
    mesh.to_mesh(skin_mask.data)
    mesh.free()
    assert len(skin_mask.data.polygons), 'Face mask lost all geometry'
    return [skin_mask]


def frame_quat(forward, across):
    forward = forward.normalized()
    across = (across - forward * across.dot(forward)).normalized()
    return Matrix((forward, across, forward.cross(across))).transposed().to_quaternion()


class SeatedPose:
    def __init__(self, arm, skin, face_mask):
        self.arm = arm
        self.skin = skin
        names = {g.index: g.name.split(':')[-1] for g in skin.vertex_groups}
        dominant = [names.get(max(v.groups, key=lambda g: g.weight).group, '') if len(v.groups) else '' for v in skin.data.vertices]
        self.hand_vertices = {side: np.array([i for i, n in enumerate(dominant) if n.startswith(prefix)])
                              for side, prefix in [(1, 'LeftHand'), (-1, 'RightHand')]}
        self.dominant = dominant
        self.finger_vertices = {b: np.array([i for i, n in enumerate(dominant) if n == b])
                                for b in ['LeftHandIndex3', 'LeftHandMiddle3', 'LeftHandThumb3']}
        self.rest = {b.name: b.matrix_basis.copy() for b in arm.pose.bones}
        self.bases = {b.name: (arm.matrix_world @ b.matrix).to_3x3().copy() for b in arm.pose.bones}
        self.head = named(arm, 'Head')
        head_world = arm.matrix_world @ self.head.matrix
        self.eye_local = head_world.inverted() @ EYE_REST
        # Mouth reference exactly as p0_people measures it (lip centre of the real face triangles).
        lips = PP.world_points(face_mask)
        lips = lips[(np.abs(lips[:, 0]) < .022) & (lips[:, 2] > 1.412) & (lips[:, 2] < 1.435)]
        self.mouth_local = head_world.inverted() @ Vector((0, float(lips[:, 1].min()), 1.425))
        self.left = ArmPose(arm, 'Left')
        self.right = ArmPose(arm, 'Right')
        self.hip_drop = SEAT_Z + HIP_JOINT_ABOVE_SEAT - (arm.matrix_world @ named(arm, 'LeftUpLeg').head).z
        self.hips_shift = Vector((0, HIPS_Y - (arm.matrix_world @ named(arm, 'Hips').head).y, self.hip_drop))
        self.rest_wrist_z = {}
        self.previous = {}

    def eye(self):
        return self.arm.matrix_world @ self.head.matrix @ self.eye_local

    def mouth(self):
        return self.arm.matrix_world @ self.head.matrix @ self.mouth_local

    def rotate(self, bone, pitch=0., yaw=0.):
        """Rotate a bone about the world X (pitch, + leans forward/down) and Z (yaw) axes of its rest frame."""
        base = self.bases[bone.name].inverted()
        bone.rotation_mode = 'QUATERNION'
        bone.rotation_quaternion = Quaternion((base @ Vector((0, 0, 1))).normalized(), math.radians(yaw)) @ \
            Quaternion((base @ Vector((1, 0, 0))).normalized(), math.radians(pitch))

    def body(self, look_at, look=1., nod=0., lean=0.):
        """Seat, lean (+ `lean` deg more in the chest), legs, and the head turned (share `look`) to the lens; nod in degrees (+ down)."""
        arm = self.arm
        for b in arm.pose.bones:
            b.matrix_basis = self.rest[b.name].copy()
        bpy.context.view_layer.update()
        hips = named(arm, 'Hips')
        self.rotate(hips, LEAN['Hips'])
        hips.location = self.bases[hips.name].inverted() @ self.hips_shift
        bpy.context.view_layer.update()
        for name in ['Spine', 'Spine1', 'Spine2']:
            self.rotate(named(arm, name), LEAN[name] + lean / 3)
        bpy.context.view_layer.update()
        self.legs()
        # Head and neck take the lean back out and turn the face to the lens; 65/35 split.
        to_lens = look_at - self.eye()
        yaw = look * math.degrees(math.atan2(to_lens.x, -to_lens.y))
        down = math.degrees(math.atan2(-to_lens.z, Vector((to_lens.x, to_lens.y)).length))
        pitch = -sum(LEAN.values()) - lean + .6 * max(down, 0.) + nod
        self.rotate(named(arm, 'Neck'), .35 * pitch, .35 * yaw)
        bpy.context.view_layer.update()
        self.rotate(self.head, .65 * pitch, .65 * yaw)
        bpy.context.view_layer.update()
        return dict(head_yaw_deg=yaw, head_pitch_deg=pitch, look_down_deg=down)

    def legs(self):
        arm = self.arm
        for side, splay in [('Left', 1), ('Right', -1)]:
            upper, lower = named(arm, side + 'UpLeg'), named(arm, side + 'Leg')
            foot, toe = named(arm, side + 'Foot'), named(arm, side + 'ToeBase')
            hip = arm.matrix_world @ upper.head
            thigh = (arm.matrix_world.to_3x3() @ (upper.tail - upper.head)).length
            shin = (arm.matrix_world.to_3x3() @ (lower.tail - lower.head)).length
            ankle_z = (arm.matrix_world @ foot.bone.head_local).z
            # Shin 6 deg back from vertical, so the foot sits under the knee; the thigh slopes to meet it.
            shin_dir = Vector((0, .105, -.995)).normalized()
            knee_z = ankle_z - shin * shin_dir.z
            drop = max(-.99, min(.99, (knee_z - hip.z) / thigh))
            thigh_dir = Vector((splay * .06, -math.sqrt(1 - drop * drop - .0036), drop)).normalized()
            orient_bone(arm, upper, thigh_dir)
            orient_bone(arm, lower, shin_dir)
            orient_bone(arm, foot, Vector((0, -.79, -.61)))
            orient_bone(arm, toe, Vector((0, -1, 0)))

    def resting(self, side):
        """Wrist, finger direction, index-to-pinky direction and elbow pole of a hand resting palm down on the table."""
        wrist = Vector((side * .23, TABLE_EDGE_Y - .10, self.rest_wrist_z.get(side, TABLE_Z + .035)))
        return wrist, Vector((-side * .25, -.95, -.03)).normalized(), Vector((-side * .95, .25, 0)), Vector((side * .55, .30, -.80))

    def rest_hand(self, side, frame):
        """Forearm on the table, hand flat beside the plate; the palm settles until its lowest skin is 1 mm above the top."""
        solver = self.left if side > 0 else self.right
        wrist, forward, across, pole = self.resting(side)
        for _ in range(1 if side in self.rest_wrist_z else 5):
            check = solver.pose(wrist, forward, across, 1, frame, pole=pole)
            check['distributed_palm_roll_degrees'] = PP.distribute_palm_roll(self.arm, solver)
            self.relax(side)
            lowest = float(PP.world_points(self.skin)[self.hand_vertices[side], 2].min())
            if side in self.rest_wrist_z or abs(lowest - TABLE_Z - .001) < .0015:
                break
            wrist.z += TABLE_Z + .001 - lowest
        self.rest_wrist_z[side] = wrist.z
        check.update(kind='resting', lowest_hand_skin_above_table_m=lowest - TABLE_Z)
        return check

    def lap_hand(self, frame):
        """Selfies: the right hand holds the phone in life; it is not demonstrated, so it rests in her lap below the table edge."""
        wrist = Vector((-.13, -.12, .71))
        check = self.right.pose(wrist, Vector((.45, -.88, -.12)).normalized(), Vector((.88, .45, 0)), 1, frame,
                                pole=Vector((-.7, .3, -.5)))
        check['distributed_palm_roll_degrees'] = PP.distribute_palm_roll(self.arm, self.right)
        self.relax(-1)
        check.update(kind='lap')
        return check

    def palm(self, side):
        arm = self.arm
        prefix = 'LeftHand' if side > 0 else 'RightHand'
        wrist = arm.matrix_world @ named(arm, prefix).head
        index = arm.matrix_world @ named(arm, prefix + 'Index1').head
        pinky = arm.matrix_world @ named(arm, prefix + 'Pinky1').head
        forward = ((index + pinky) / 2 - wrist).normalized()
        radial = (index - pinky).normalized()
        radial = (radial - forward * radial.dot(forward)).normalized()
        palm = (forward.cross(radial) if side > 0 else radial.cross(forward)).normalized()
        return wrist, forward, radial, palm

    def relax(self, side, amount=1.):
        """Resting palm down: fingers curl a little into the palm, the thumb lies flat toward the other hand."""
        arm = self.arm
        prefix = 'LeftHand' if side > 0 else 'RightHand'
        _, forward, _, palm = self.palm(side)
        for finger in ['Index', 'Middle', 'Ring', 'Pinky']:
            for joint, degrees in enumerate((6, 14, 14), 1):
                bone = named(arm, prefix + finger + str(joint))
                theta = math.radians(degrees)
                now = (arm.matrix_world.to_3x3() @ (bone.tail - bone.head)).normalized()
                orient_bone(arm, bone, now.lerp(forward * math.cos(theta) + palm * math.sin(theta), amount).normalized())
        flat = Vector((forward.x, forward.y, 0)).normalized()
        inward = Vector((-side, 0, 0))
        for joint, (f, i, d) in enumerate([(.45, .85, .15), (.70, .70, .05), (.85, .50, .05)], 1):
            bone = named(arm, prefix + 'Thumb' + str(joint))
            now = (arm.matrix_world.to_3x3() @ (bone.tail - bone.head)).normalized()
            orient_bone(arm, bone, now.lerp((flat * f + inward * i + Vector((0, 0, -d))).normalized(), amount).normalized())

    def key(self, frame):
        for bone in self.arm.pose.bones:
            bone.rotation_mode = 'QUATERNION'
            previous = self.previous.get(bone.name)
            if previous and previous.dot(bone.rotation_quaternion) < 0:
                bone.rotation_quaternion.negate()
            self.previous[bone.name] = bone.rotation_quaternion.copy()
            bone.keyframe_insert('rotation_quaternion', frame=frame)
            bone.keyframe_insert('location', frame=frame)


def wound_spaghetti(G):
    """A small nest of spaghetti twirled round the tines: tilted closed loops, so no strand end hangs free."""
    loops = []
    for y, radius, tilt, phase in [(.041, .0165, 14., 0.), (.047, .0180, -18., 1.3), (.053, .0150, 6., 2.1)]:
        lift = .010 * ((y - .015) / .047) ** 2 + .0011         # the tine bend at this depth (A.fork)
        loops.append([(radius * math.cos(a), y + math.tan(math.radians(tilt)) * radius * math.cos(a) + .0012 * math.sin(3 * a + phase),
                       lift + radius * .78 * math.sin(a)) for a in [k / 16 * math.tau for k in range(16)]])
    # One strand hangs below the nest as a closed U (both ends tucked into the nest), so it reads as spaghetti.
    loops.append([(.006 * math.sin(a) + .002 * math.sin(2 * a), .047 + .003 * math.sin(a), -.003 - .013 * (1 - math.cos(a)))
                  for a in [k / 14 * math.tau for k in range(14)]])
    strands = []
    for points in loops:
        data = bpy.data.curves.new('Wound spaghetti', 'CURVE')
        data.dimensions, data.resolution_u, data.bevel_depth, data.bevel_resolution = '3D', 12, .0018, 3
        spline = data.splines.new('BEZIER')
        spline.bezier_points.add(len(points) - 1)
        for point, location in zip(spline.bezier_points, points):
            point.co = location
            point.handle_left_type = point.handle_right_type = 'AUTO'
        spline.use_cyclic_u = True
        obj = bpy.data.objects.new('Wound spaghetti', data)
        bpy.context.collection.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.convert(target='MESH')
        obj = G.finish(bpy.context.object, 'Wound spaghetti')
        obj.select_set(False)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        strands.append(obj)
    return strands


def reachable(solver, arm, wrist, margin=.97):
    shoulder = arm.matrix_world @ solver.upper.head
    delta = wrist - shoulder
    limit = (solver.a + solver.b) * margin
    return shoulder + delta.normalized() * limit if delta.length > limit else wrist


def regions(skin):
    """Dominant deforming bone family per skin vertex: arm (arm, forearm, hand, fingers), leg, or torso and head."""
    names = {g.index: g.name.split(':')[-1] for g in skin.vertex_groups}
    region = np.zeros(len(skin.data.vertices), dtype='<U5')
    for v in skin.data.vertices:
        best = max(v.groups, key=lambda g: g.weight, default=None)
        name = names.get(best.group, '') if best else ''
        region[v.index] = 'arm' if ('Arm' in name or 'Hand' in name) else 'leg' if ('Leg' in name or 'Foot' in name or 'Toe' in name) else 'body'
    return region


def contact_report(skin, region, chair, table_centre):
    """Skin inside the table slab or the chair seat, per body region; legs below the floor."""
    p = PP.world_points(skin)
    radial = np.linalg.norm(p[:, :2] - np.array(table_centre[:2]), axis=1)
    inside = radial < TABLE_RADIUS
    slab = inside & (p[:, 2] > TABLE_Z - .035) & (p[:, 2] < TABLE_Z - .003)
    seat = (np.abs(p[:, 0] - chair.x) < .19) & (np.abs(p[:, 1] - chair.y) < .16) & (p[:, 2] > SEAT_Z - .06)
    out = dict(below_floor=int((p[:, 2] < -.005).sum()), lowest_skin_z=float(p[:, 2].min()))
    for name in ['arm', 'leg', 'body']:
        r = region == name
        out[name + '_in_table_slab'] = int((slab & r).sum())
        sunk = p[seat & r]
        out[name + '_seat_sink_m'] = float(max(0., SEAT_Z - sunk[:, 2].min())) if len(sunk) else None
    under = p[inside & (region == 'leg') & (p[:, 2] < TABLE_Z - .035)]
    out['leg_clearance_under_table_m'] = float(TABLE_Z - .035 - under[:, 2].max()) if len(under) else None
    front = p[(region == 'body') & (np.abs(p[:, 0]) < .16) & (p[:, 2] > TABLE_Z - .04) & (p[:, 2] < TABLE_Z + .06)]
    out['belly_gap_to_table_edge_m'] = float(front[:, 1].min() - (table_centre.y + TABLE_RADIUS)) if len(front) else None
    return out


def place_camera(camera, eye, lens):
    """Lens position and aim with the eyes one third from the top of a portrait frame."""
    kind, distance, height, side = camera
    above_axis = math.degrees(math.atan((1 - 2 * EYE_FROM_TOP) * 18 / lens))
    yaw = math.radians(side)  # positive puts the lens to her right (-X)
    if kind == 'hand':
        horizontal = math.sqrt(distance ** 2 - height ** 2)
        position = eye + Vector((-math.sin(yaw) * horizontal, -math.cos(yaw) * horizontal, height))
        toward = (eye - position).normalized()
        right = toward.cross(Vector((0, 0, 1))).normalized()
        axis = Quaternion(right, -math.radians(above_axis)) @ toward
    else:
        # Rear camera propped on its bottom edge, leaning back 7.5 deg against a cup; lens 13 cm over the table.
        lens_z = TABLE_Z + .13
        horizontal = math.sqrt(distance ** 2 - (eye.z - lens_z) ** 2)
        position = Vector((eye.x - math.sin(yaw) * horizontal, eye.y - math.cos(yaw) * horizontal, lens_z))
        flat = Vector((eye.x - position.x, eye.y - position.y, 0)).normalized()
        axis = (flat * math.cos(math.radians(7.5)) + Vector((0, 0, 1)) * math.sin(math.radians(7.5))).normalized()
    target = position + axis * distance
    measured = dict(eye=list(eye), eye_height_m=eye.z, lens_position=list(position), lens_mm=lens,
                    lens_to_eye_m=(eye - position).length, lens_above_eye_m=position.z - eye.z,
                    lens_above_table_m=position.z - TABLE_Z,
                    pitch_deg=math.degrees(math.asin(-axis.z)), eye_above_axis_deg=math.degrees(axis.angle(eye - position)))
    return position, target, measured


def build(gid, record, P):
    A, V, G = P.A, P.V, P.G
    spec = GUIDES[gid]
    act = spec['act']
    root, arm, face = PP.load_creator(P)
    face = trim_face_mask(face)
    face_mask = face[0]
    skin = next(o for o in P.members(root) if o.name.startswith('Canonical creator continuous'))
    region = regions(skin)
    front = record['camera'] == 'front'
    state = dict(hero=face, actions=[], contacts=[], adaptations=[], camera_height_support=0., hand_count=2,
                 silhouettes=0, detailed_people=1, framing_masks=face, character_root=root, preview_mirrored=front,
                 lens_mm=FRONT_LENS if front else REAR_LENS, performance_checks=[], light_position=(-.8, -.7, 2.0),
                 character_fade_floor=FADE_FLOOR)
    seated = SeatedPose(arm, skin, face_mask)
    chair_y = HIPS_Y + .03
    chair = V.chair((0, chair_y, 0))
    P.role(chair, 'background')
    chair['p0_seated_chair'] = True
    table_centre = Vector((0, TABLE_EDGE_Y - TABLE_RADIUS, 0))
    table = A.table(tuple(table_centre), TABLE_RADIUS)
    P.role(table, 'background')
    table['p0_seated_table'] = True
    V.window((-.85, 1.75, 1.5))
    V.pendant((.75, 1.4, 2.3))
    P.role(V.plant((-.73, 1.30, 0), height=1.1), 'background')

    # Place setting and the held prop. Personal dishes sit at her place, never the table centre.
    prop = cup_points = plate = None
    if act == 'sip':
        saucer = A.saucer(tuple(CUP_AT))
        P.role(saucer, 'support')
        prop, extra = P.cup(CUP_AT.x, CUP_AT.y, TABLE_Z, False)
        for o in [extra, *extra.children_recursive]:
            bpy.data.objects.remove(o, do_unlink=True)
        prop.scale = (CUP_SCALE,) * 3
        P.role(prop, 'support')
        prop['p0_held_cup'] = True
        prop['p0_grip_style'] = 'cup_handle_thumb_above'
        prop['p0_face_gap_m'] = CUP_FACE_GAP
        bpy.context.view_layer.update()
        inverse = np.array(prop.matrix_world.inverted())
        cup_points = np.concatenate([PP.world_points(o) @ inverse[:3, :3].T + inverse[:3, 3] for o in P.members(prop)])
        start_point = Vector((CUP_AT.x, CUP_AT.y, TABLE_Z + .010 + .118 * CUP_SCALE))   # rim centre, cup on its saucer
    elif act == 'bite':
        plate = A.pasta(tuple(PLATE_AT))
        P.role(plate, 'support')
        prop = A.fork((.15, -.22, 1.22), role='support')
        for food in wound_spaghetti(G):
            A.tag(food, 'support', 'Spaghetti wound round the tines, closed loops with no loose ends; stops at the lips')
            food.parent = prop
        prop['p0_held_fork'] = True
        prop['p0_grip_style'] = 'fork_pencil_tines_up' if spec.get('grip') == 'tripod' else 'fork_tripod_side_lift'
        prop['p0_grip_local'] = list(FORK_GRIP)
        prop['p0_face_gap_m'] = FORK_FACE_GAP
        bpy.context.view_layer.update()
        inverse = np.array(prop.matrix_world.inverted())
        fork_points = np.concatenate([PP.world_points(o) @ inverse[:3, :3].T + inverse[:3, 3] for o in P.members(prop)])
        # The loaded fork waits 7 cm over the near half of her plate, tines down.
        start_point = Vector((PLATE_AT.x + .05, PLATE_AT.y + .04, TABLE_Z + .07))
    else:
        if act != 'plate':
            plate = A.pasta(tuple(SETTING_PLATE_AT))
            P.role(plate, 'support')
        else:
            plate = A.pasta((0, -.4, 1.))   # placed by the waiter grip each frame
            plate.scale = (PLATE_SCALE,) * 3
            P.role(plate, 'support')
            plate['p0_held_plate'] = True
        fork = A.fork((.33, TABLE_EDGE_Y - .36, TABLE_Z + .004))
        P.role(fork, 'support')
        cup, saucer = P.cup(-.27, TABLE_EDGE_Y - .52, TABLE_Z, False)
        P.role(cup, 'support')
        P.role(saucer, 'support')

    # Pose toward a provisional lens, measure the eye, place the camera; repeat with the head turned to it.
    position = Vector((0, -1., 1.18))
    for _ in range(3):
        seated.body(position, spec['look'])
        eye = seated.eye()
        position, target, measured = place_camera(spec['camera'], eye, state['lens_mm'])
    measured.update(table_edge_y=TABLE_EDGE_Y, chair_y=chair_y, fade_floor_m=FADE_FLOOR)
    eye0 = eye.copy()

    def aim_at_lips(margin=0.):
        """The tine axis points at the lips; the fork stops where its nearest point (the wound pasta) is the face gap away."""
        bite_rotation = FORK_AT_MOUTH.to_track_quat('Y', 'Z')
        axis = bite_rotation @ Vector((0, 1, 0))
        face = BVHTree.FromPolygons([Vector(v) for v in PP.world_points(face_mask)], [tuple(f.vertices) for f in face_mask.data.polygons])
        rotated = [bite_rotation @ (Vector(p) - FORK_TIP) for p in fork_points[::2]]
        mouth = seated.mouth()
        for reach in np.arange(0., .15, .0005):
            tip = mouth - axis * float(reach)
            gap = min(face.find_nearest(tip + p)[3] for p in rotated)
            if gap >= FORK_FACE_GAP + margin:
                break
        bite_reach.update(reach=float(reach), gap=gap, axis=axis)

    def hold_prop(u, frame):
        """p0_people's approved cup and fork grips; the reach starts at her place setting instead of the chest."""
        phase = P.smooth((u - .12) / .35) * (1 - P.smooth((u - .72) / .22))
        mouth = seated.mouth()
        left = seated.left
        if act == 'sip':
            point_local = Vector((0, 0, .118))
            goal = start_point.lerp(mouth + Vector((0, -.033, -.008)), phase)
            prop.rotation_euler = (math.radians(-5) * phase, 0, 0)
            rotation = np.array(prop.rotation_euler.to_matrix())
            offsets = (cup_points * CUP_SCALE - np.array(point_local) * CUP_SCALE) @ rotation.T
            cloud = PP.world_points(face_mask)
            near = cloud[(cloud[:, 0] > goal.x + offsets[:, 0].min() - .003) & (cloud[:, 0] < goal.x + offsets[:, 0].max() + .003) &
                         (cloud[:, 2] > mouth.z - .08) & (cloud[:, 2] < mouth.z + .005)]
            if len(near):
                # Never closer to the face than the approved 6 mm gap.
                goal.y = min(goal.y, float(near[:, 1].min() - CUP_FACE_GAP - offsets[:, 1].max()))
            forward, across = None, Vector((0, 0, 1))
            pole = Vector((.6, 0, -1))
        else:
            point_local = FORK_TIP
            if 'reach' not in bite_reach:
                aim_at_lips()
            goal = start_point.lerp(mouth - bite_reach['axis'] * bite_reach['reach'], phase)
            # Over the plate the tines point down into the food; the hand turns up into the approved bite angle as it rises.
            forward = Vector((-.45, -.80, -.30)).normalized().lerp(HAND_AT_MOUTH.normalized(), phase).normalized()
            fork_rotation = FORK_OVER_PLATE.to_track_quat('Y', 'Z').slerp(FORK_AT_MOUTH.to_track_quat('Y', 'Z'), phase)
            across = Vector((0, 0, 1))
            pole = BITE_POLE if spec.get('low_elbow') else -forward
            if spec.get('grip') == 'tripod':
                return tripod_hold(goal, fork_rotation, phase, frame, mouth)
        # Same start guess on every frame, so the identical target frames solve identically.
        wrist = goal + Vector((.10, .06, -.06))
        if act == 'bite':
            wrist += fork_rotation @ (FORK_GRIP - Vector((0, .005, 0)))
        for iteration in range(40):
            wrist = reachable(left, arm, wrist)
            for bone in [left.upper, left.fore, left.hand]:
                bone.matrix_basis = seated.rest[bone.name].copy()
            bpy.context.view_layer.update()
            actual_forward = PP.forearm_forward(arm, left, wrist, pole) if act == 'sip' else forward
            if act == 'bite' and spec.get('low_elbow'):
                fore = PP.forearm_forward(arm, left, wrist, pole)
                bend = fore.angle(forward)
                if bend > math.radians(BITE_WRIST_BEND):
                    actual_forward = fore.slerp(forward, math.radians(BITE_WRIST_BEND) / bend)
            check = left.pose(wrist, actual_forward, across, 1, frame, pole=pole)
            check['distributed_palm_roll_degrees'] = PP.distribute_palm_roll(arm, left)
            contact = PP.grip_digits(arm, left, 'cup' if act == 'sip' else 'fork')
            if act == 'sip':
                prop.location = contact - prop.rotation_euler.to_matrix() @ (Vector((.081, .003, .096)) * CUP_SCALE)
            else:
                prop.rotation_euler = fork_rotation.to_euler()
                prop.location = contact - prop.rotation_euler.to_matrix() @ FORK_GRIP
            bpy.context.view_layer.update()
            error = goal - prop.matrix_world @ point_local
            if error.length < .0005:
                break
            step = error * (.65 if act == 'sip' else 1)
            if step.length > .04:
                step = step.normalized() * .04
            wrist = wrist + step
        assert error.length < .003, ('Prop did not reach its target', gid, u, error.length, tuple(error), tuple(wrist), tuple(arm.matrix_world @ left.upper.head), tuple(goal), tuple(contact))
        check.update(kind=act, phase=phase, prop_target_error_m=error.length, prop_contact=list(contact), face_reference=list(mouth))
        if act == 'bite':
            check.update(fork_grip_from_tine_tips_m=(point_local - FORK_GRIP).y, bite_tip_to_lips_m=bite_reach['reach'],
                         bite_face_gap_m=bite_reach['gap'])
        prop.keyframe_insert('location', frame=frame)
        prop.keyframe_insert('rotation_euler', frame=frame)
        return check

    bite_reach = {}
    tripod = {}
    digit_ids = {n: np.array([i for i, b in enumerate(seated.dominant) if b == n])
                 for n in set(seated.dominant) if n.startswith('LeftHand') and n != 'LeftHand'}
    grip_centre = Vector((0, FORK_GRIP.y, 0))

    def fork_local(points):
        m = np.array(prop.matrix_world.inverted())
        return points @ m[:3, :3].T + m[:3, 3]

    def clearance(ids):
        return float(fork_clearance(fork_local(PP.world_points(skin)[ids])).min())

    def bend_finger(finger, angle, basis):
        total = 0.
        for joint, share in enumerate(TRIPOD_FLEX[finger], 1):
            total += angle * share
            t = math.radians(total)
            orient_bone(arm, named(arm, 'LeftHand' + finger + str(joint)), basis.col[0] * math.cos(t) + basis.col[2] * math.sin(t))

    def bisect(at, low, high, gap):
        """Largest value in [low, high] at which `at` (a clearance) stays at least `gap`; the pose is left there."""
        if at(high) >= gap:
            return high
        if at(low) < gap:
            return low
        for _ in range(10):
            mid = (low + high) / 2
            if at(mid) >= gap:
                low = mid
            else:
                high = mid
        at(low)
        return low

    def close_finger(finger, basis, limit, gap=CONTACT_GAP):
        """MCP flexion (later joints at their TRIPOD_FLEX share) up to `limit` deg, stopping at first contact with the fork."""
        ids = np.concatenate([digit_ids['LeftHand' + finger + str(j)] for j in (1, 2, 3)])

        def at(angle):
            bend_finger(finger, angle, basis)
            return clearance(ids)
        return bisect(at, 0., limit, gap)

    def place_thumb(basis):
        """Thumb pad on the handle's palm-side edge at the grip (FG2, FG4); the web stays open and round (FG3)."""
        ids = np.concatenate([digit_ids['LeftHandThumb2'], digit_ids['LeftHandThumb3']])
        world = prop.matrix_world
        side = 1. if (world.to_3x3().transposed() @ basis.col[2]).x > 0 else -1.     # the handle edge on the palm side

        def at(inward):
            target = world @ Vector((side * (.0089 + .02 - inward), FORK_GRIP.y, 0))
            first = named(arm, 'LeftHandThumb1')
            orient_bone(arm, first, (target + basis.col[1] * .012 - arm.matrix_world @ first.head).normalized())
            for joint in (2, 3):
                bone = named(arm, 'LeftHandThumb' + str(joint))
                orient_bone(arm, bone, (target - arm.matrix_world @ bone.head).normalized())
            return clearance(ids)
        return bisect(at, 0., .02, CONTACT_GAP), side

    def tripod_hold(goal, fork_rotation, phase, frame, mouth):
        """Pencil hold (fork_grip.md): the hand is set by the fork, each finger closes onto the handle until it touches."""
        left = seated.left
        axis = TRIPOD_AXIS.normalized()
        top = (TRIPOD_TOP - axis * TRIPOD_TOP.dot(axis)).normalized()
        # Columns: hand forward, radial and palm in the fork's axes.
        hand_in_fork = Matrix.Rotation(math.radians(TRIPOD_ROLL), 3, 'Y') @ Matrix((axis.cross(top), axis, top))
        # Over the plate the fork follows the hand (the grip sets it); it turns into the approved angle at the lips.
        over_plate = (frame_quat(*TRIPOD_HAND_OVER_PLATE).to_matrix() @ hand_in_fork.transposed()).to_quaternion()
        fork_rotation = over_plate.slerp(FORK_AT_MOUTH.to_track_quat('Y', 'Z'), phase)
        goal = goal + TRIPOD_START_SHIFT * (1 - phase)
        R = fork_rotation.to_matrix()
        origin = goal - R @ FORK_TIP
        if not tripod:
            # The middle finger's distal phalanx in hand coordinates (pose independent), curled to its support angle.
            basis = R @ hand_in_fork
            left.pose(reachable(left, arm, origin + R @ grip_centre - basis.col[0] * .12), basis.col[0], basis.col[1], 1, frame, pole=BITE_POLE)
            PP.distribute_palm_roll(arm, left)
            bend_finger('Middle', TRIPOD_CURL['Middle'], basis)
            middle = PP.world_points(skin)[digit_ids['LeftHandMiddle3']] - np.array(arm.matrix_world @ left.hand.head)
            tripod.update(middle=middle @ np.array(basis), digits={})

        def relation(roll):
            """Hand axes and wrist in fork coordinates when the fingers hold the handle rolled `roll` deg about its axis:
            the handle's underside rests on the top of the middle finger's distal phalanx (FG2)."""
            hand = Matrix.Rotation(math.radians(roll), 3, 'Y') @ hand_in_fork
            up = np.array(hand.transposed() @ Vector((0, 0, 1)))
            support = Vector(tripod['middle'][np.argmax(tripod['middle'] @ up)])
            fork_origin = support - hand.transposed() @ Vector((0, TRIPOD_SUPPORT_Y, -.0011 - CONTACT_GAP))
            return hand, -(hand @ fork_origin)

        shoulder = arm.matrix_world @ left.upper.head
        choice = None
        # The fingers roll the handle a little about its axis only when the wrist would pass its limit.
        for roll in sorted(range(-30, 31), key=lambda r: (abs(r), r)):
            hand, wrist_in_fork = relation(roll)
            basis = R @ hand
            wrist = origin + R @ wrist_in_fork
            if (wrist - shoulder).length > (left.a + left.b) * .97:
                continue
            bend = math.degrees(PP.forearm_forward(arm, left, wrist, BITE_POLE).angle(basis.col[0]))
            ok = bend <= BITE_WRIST_BEND + 3 and basis.col[1].z > TRIPOD_INDEX_UP
            if ok or choice is None or bend < choice[1]:
                choice = (roll, bend, basis, wrist, wrist_in_fork)
            if ok:
                break
        roll, bend, basis, wrist, wrist_in_fork = choice
        assert bend < 45, ('Tripod grip wrist bend', bend, phase)
        check = left.pose(wrist, basis.col[0], basis.col[1], 1, frame, pole=BITE_POLE)
        check['distributed_palm_roll_degrees'] = PP.distribute_palm_roll(arm, left)
        prop.rotation_euler = fork_rotation.to_euler()
        prop.location = arm.matrix_world @ left.hand.head - R @ wrist_in_fork
        bpy.context.view_layer.update()
        digit_bones = [b for b in arm.pose.bones if b.name.split(':')[-1].startswith(tuple('LeftHand' + f for f in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']))]
        solved_digits = tripod['digits'].get(roll)
        if solved_digits:
            for b in digit_bones:
                b.matrix_basis = solved_digits['bones'][b.name].copy()
            bpy.context.view_layer.update()
        else:
            # Middle first (the support), then the index pad on top, the thumb on the side, ring and little curled under.
            bend_finger('Middle', TRIPOD_CURL['Middle'], basis)
            angles = dict(Middle=TRIPOD_CURL['Middle'], Index=close_finger('Index', basis, 80.))
            angles['thumb_inward_m'], side = place_thumb(basis)
            for finger in ['Ring', 'Pinky']:
                angles[finger] = close_finger(finger, basis, TRIPOD_CURL[finger], .002)
            solved_digits = dict(bones={b.name: b.matrix_basis.copy() for b in digit_bones}, angles=angles, thumb_side=side)
            tripod['digits'][roll] = solved_digits
        error = goal - prop.matrix_world @ FORK_TIP
        assert error.length < .003, ('Fork did not reach its target', gid, phase, error.length)
        points = PP.world_points(skin)
        local = fork_local(points[seated.hand_vertices[1]])
        depth = fork_clearance(local)
        gaps = {f: float(fork_clearance(fork_local(points[np.concatenate([digit_ids['LeftHand' + f + str(j)] for j in (1, 2, 3)])])).min())
                for f in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']}
        web = (arm.matrix_world @ named(arm, 'LeftHandThumb3').tail + arm.matrix_world @ named(arm, 'LeftHandIndex2').tail) / 2
        web_local = prop.matrix_world.inverted() @ web
        if 'p0_grip_local_set' not in tripod:
            prop['p0_grip_local'] = list(web_local)
            tripod['p0_grip_local_set'] = True
        elbow = arm.matrix_world @ left.fore.head
        check.update(kind=act, grip='tripod', phase=phase, roll_in_fingers_deg=roll, wrist_bend_deg=bend,
                     prop_target_error_m=error.length, face_reference=list(mouth), finger_angles=solved_digits['angles'],
                     max_hand_depth_into_fork_m=float(max(0., -depth.min())), finger_gap_to_fork_m=gaps,
                     web_point_fork_local=list(web_local), elbow_above_table_m=elbow.z - TABLE_Z,
                     bite_tip_to_lips_m=bite_reach['reach'], bite_face_gap_m=bite_reach['gap'])
        prop.keyframe_insert('location', frame=frame)
        prop.keyframe_insert('rotation_euler', frame=frame)
        return check

    def gesture(u, frame):
        """The approved open-palm verdict, rising from the hand resting on the table; the palm turns to the lens."""
        g = P.smooth((u - .10) / .32) * (1 - P.smooth((u - .64) / .30))
        left = seated.left
        if 1 not in seated.rest_wrist_z:
            seated.rest_hand(1, frame)
            for bone in arm.pose.bones:
                if bone.name.split(':')[-1].startswith(('LeftArm', 'LeftForeArm', 'LeftHand')):
                    bone.matrix_basis = seated.rest[bone.name].copy()
            bpy.context.view_layer.update()
        wrist0, forward0, across0, pole0 = seated.resting(1)
        wrist1 = eye0 + GESTURE_FROM_EYE
        to_lens = position - wrist1
        to_lens = Vector((to_lens.x, to_lens.y, 0)).normalized()
        forward1 = Vector((0, 0, 1))
        across1 = to_lens.cross(forward1)          # palm normal (forward x across) faces the lens
        q = frame_quat(forward0, across0).slerp(frame_quat(forward1, across1), g).to_matrix()
        pole = pole0.lerp(Vector((.9, .08, -.8)), g)
        check = left.pose(wrist0.lerp(wrist1, g), q.col[0], q.col[1], 1, frame, pole=pole)
        check['distributed_palm_roll_degrees'] = PP.distribute_palm_roll(arm, left)
        seated.relax(1, 1 - g)
        check.update(kind='gesture', gesture=g)
        return check

    def profile(points, r):
        r = min(max(r, 0.), points[-1][0])
        for (r0, z0), (r1, z1) in zip(points, points[1:]):
            if r0 <= r <= r1:
                return z0 + (z1 - z0) * (r - r0) / max(r1 - r0, 1e-9)
        return points[-1][1]

    lens_tan = 18 / state['lens_mm']
    cam_forward = (target - position).normalized()
    cam_right = cam_forward.cross(Vector((0, 0, 1))).normalized()
    cam_up = cam_right.cross(cam_forward)

    def rows(points):
        out = []
        for p in points:
            d = p - position
            out.append((.5 - (d.dot(cam_up) / d.dot(cam_forward)) / (2 * lens_tan),
                        .5 + (d.dot(cam_right) / d.dot(cam_forward)) / (2 * lens_tan * 405 / 720)))
        return out

    def plate_pose(centre, tilt):
        to_lens = position - centre
        h = Vector((to_lens.x, to_lens.y, 0)).normalized()
        n = (Vector((0, 0, 1)) * math.cos(math.radians(tilt)) + h * math.sin(math.radians(tilt))).normalized()
        return n, n.to_track_quat('Z', 'Y')

    def rim(centre, tilt):
        n, q = plate_pose(centre, tilt)
        return [centre + q @ Vector((RIM_R * math.cos(a), RIM_R * math.sin(a), .029 * PLATE_SCALE)) for a in [k * math.tau / 48 for k in range(48)]]

    def grip_side(centre, n):
        to_lens = position - centre
        h = Vector((to_lens.x, to_lens.y, 0)).normalized()
        side = Vector((1, 0, 0)) * math.cos(math.radians(GRIP_SIDE)) + h * math.sin(math.radians(GRIP_SIDE))
        return (side - n * side.dot(n)).normalized()

    def choose_plate():
        """At her left shoulder height, beside or just below her face, shoulder height first: the first tilt (owner 20-30 deg) whose rim fits the band, clear of
        her mouth and chin in frame and of her head and shoulder in space, with the grip in reach of the left shoulder."""
        shoulder = arm.matrix_world @ seated.left.upper.head
        points = PP.world_points(skin)
        body = points[region != 'arm']
        eye = seated.eye()
        lower = PP.world_points(face_mask)
        lower = lower[(lower[:, 2] < eye.z - .05) & (np.abs(lower[:, 0] - eye.x) < .045)]   # mouth and chin only
        box = rows([Vector(p) for p in lower[::max(1, len(lower) // 400)]])
        chin_right = max(x for _, x in box)
        chin_rows = (min(y for y, _ in box), max(y for y, _ in box))
        chin_cols = (min(x for _, x in box), chin_right)
        DIAG = {}
        shoulder_z = shoulder.z
        rel_b = body - np.array(position)
        b_depth = rel_b @ np.array(cam_forward)
        b_rows = .5 - (rel_b @ np.array(cam_up)) / b_depth / (2 * lens_tan)
        b_cols = .5 + (rel_b @ np.array(cam_right)) / b_depth / (2 * lens_tan * 405 / 720)
        for tilt in PLATE_TILTS:
            for dz in (.04, .01, .07, -.02, .10):                 # shoulder height first
                for x in (.16, .20, .12, .24, .28, .08, .32):
                    for y in (-.26, -.30, -.34, -.38, -.22, -.42):
                        centre = Vector((x, y, shoulder_z + dz))
                        r = rows(rim(centre, tilt))
                        top, bottom = min(v for v, _ in r), max(v for v, _ in r)
                        left_edge, right_edge = min(v for _, v in r), max(v for _, v in r)
                        why = 'band' if (bottom > PLATE_BAND[1] or top < PLATE_BAND[0]) else 'edge' if right_edge > .985 else 'chin' if (left_edge < chin_cols[1] + .015 and right_edge > chin_cols[0] - .015 and top < chin_rows[1] + .015) else None
                        DIAG[why] = DIAG.get(why, 0) + 1
                        if why:
                            continue
                        n, q = plate_pose(centre, tilt)
                        grip = centre + grip_side(centre, n) * (RIM_R + .03) - n * .05
                        if not .18 < (grip - shoulder).length < .34:
                            DIAG['reach'] = DIAG.get('reach', 0) + 1
                            continue
                        # Nothing of her body inside or just around the plate, and nothing of her body nearer the lens
                        # inside the plate's outline (the plate is never behind her shoulder, hair or chin).
                        rel = body - np.array(centre)
                        hz = rel @ np.array(n)
                        rr = np.linalg.norm(rel - np.outer(hz, np.array(n)), axis=1)
                        if ((rr < RIM_R + .02) & (hz > -.04) & (hz < .05)).any():
                            DIAG['touch'] = DIAG.get('touch', 0) + 1
                            continue
                        inside = (b_rows > top) & (b_rows < bottom) & (b_cols > left_edge) & (b_cols < right_edge)
                        if (inside & (b_depth < (centre - position).dot(cam_forward))).any():
                            DIAG['behind'] = DIAG.get('behind', 0) + 1
                            continue
                        return centre, tilt, (top, bottom, left_edge, right_edge, chin_rows[1])
        print('DIAG', DIAG, 'chin_right', chin_right)
        raise AssertionError('No held-plate placement fits the band beside her face')

    plate_choice = {}
    grip_cache = {}

    def hold_plate(u, frame):
        """Waiter grip: index and middle fingertips under the rim, thumb pad on the rim top; the hand stays outside the plate."""
        g = P.smooth((u - .10) / .32) * (1 - P.smooth((u - .64) / .30))
        if not plate_choice:
            plate_choice.update(zip(('centre', 'tilt', 'band'), choose_plate()))
        # She turns the dish 15 deg in her hand to show it: the grip travels along the rim, the band (a circle) stays put.
        tilt = plate_choice['tilt']
        centre = plate_choice['centre'].copy()
        n, q = plate_pose(centre, tilt)
        turn = Quaternion(n, math.radians(PLATE_TURN * g))
        plate.rotation_euler = (turn @ q).to_euler()
        plate.location = centre
        bpy.context.view_layer.update()
        # Grip on the outer rim, turned toward the lens: palm up under the plate, fingers pointing in along the underside,
        # the thumb over the rim. The lens sees the thumb, the index side and the knuckles of the hand.
        d = turn @ grip_side(centre, n)
        palm_dir = n
        left = seated.left
        forward = (-d + n * .12).normalized()
        forward = (forward - palm_dir * forward.dot(palm_dir)).normalized()
        across = palm_dir.cross(forward)
        verts = seated.hand_vertices[1]
        names = seated.finger_vertices

        def pads(points, bone, top=True):
            sel = points[names[bone]]
            tail = np.array(arm.matrix_world @ named(arm, bone.replace('LeftHand', 'LeftHand')).tail)
            sel = sel[np.linalg.norm(sel - tail, axis=1) < .016]       # the pad at the tip, not the whole phalanx
            heights = (sel - np.array(centre)) @ np.array(n)
            pick = sel[np.argsort(heights)[-3:]] if top else sel[np.argsort(heights)[:3]]
            p = Vector(pick.mean(axis=0))
            rel = p - centre
            hgt = rel.dot(n)
            r = (rel - n * hgt).length
            return p, r, hgt

        def plate_depth(pts):
            rel = pts - np.array(centre)
            hz = rel @ np.array(n)
            rr = np.linalg.norm(rel - np.outer(hz, np.array(n)), axis=1)
            under = np.interp(rr, [p[0] for p in PLATE_UNDER], [p[1] for p in PLATE_UNDER])
            top = np.interp(rr, [p[0] for p in PLATE_TOP], [p[1] for p in PLATE_TOP])
            return np.where(rr < RIM_R, np.minimum(hz - under, top - hz), -1.)

        flexes = {'Index': [12., 22., 14.], 'Middle': [12., 22., 14.], 'Ring': [75., 100., 80.], 'Pinky': [75., 100., 80.]}   # ring and pinky tuck into the palm

        def curl(finger, hand_forward, palm):
            for joint, degrees in enumerate(flexes[finger], 1):
                t = math.radians(degrees)
                orient_bone(arm, named(arm, 'LeftHand' + finger + str(joint)), hand_forward * math.cos(t) + palm * math.sin(t))

        plate_matrix = Matrix.Translation(centre) @ (turn @ q).to_matrix().to_4x4()
        hand_bones = [b for b in arm.pose.bones if b.name.split(':')[-1].startswith(('LeftHandIndex', 'LeftHandMiddle', 'LeftHandRing', 'LeftHandPinky', 'LeftHandThumb'))]
        if not grip_cache:
            # Solve the grip once, on the target frame; the hand then stays fixed to the plate while she turns it.
            wrist = reachable(left, arm, centre + d * (RIM_R + .03) - n * .05)
            for iteration in range(25):
                check = left.pose(wrist, forward, across, 1, frame, pole=PLATE_POLE)
                check['distributed_palm_roll_degrees'] = PP.distribute_palm_roll(arm, left)
                _, hand_forward, radial, palm = seated.palm(1)
                for finger in ['Index', 'Middle', 'Ring', 'Pinky']:
                    curl(finger, hand_forward, palm)
                points = PP.world_points(skin)
                both = [pads(points, b)[0] for b in ['LeftHandIndex3', 'LeftHandMiddle3']]
                pad = (both[0] + both[1]) / 2
                goal = centre + d * FINGER_R + n * (profile(PLATE_UNDER, abs(FINGER_R)) - .001)
                # Move the hand (damped) so the two fingertip pads meet the underside at the grip radius.
                error = goal - pad
                if error.length < .0008:
                    break
                step = error * .7
                if step.length > .03:
                    step = step.normalized() * .03
                wrist = reachable(left, arm, wrist + step)
            # Each fingertip pad settles against the underside (0.5 mm gap) by its own knuckle flexion.
            _, hand_forward, radial, palm = seated.palm(1)
            for finger in ['Index', 'Middle']:
                for _ in range(10):
                    curl(finger, hand_forward, palm)
                    # The deepest point of the fingertip, not only its pad, stays 0.5 mm clear of the plate.
                    gap_ = -float(plate_depth(PP.world_points(skin)[names['LeftHand' + finger + '3']]).max()) - .0005
                    if abs(gap_) < .0004:
                        break
                    flexes[finger][0] += math.degrees(gap_ / .07)
                    flexes[finger][1] += math.degrees(gap_ / .07) * .5
            # Ring and pinky take the curl (from relaxed to tucked) that keeps them farthest from the plate.
            for finger in ['Ring', 'Pinky']:
                chain = np.array([i for i, b in enumerate(seated.dominant) if b.startswith('LeftHand' + finger)])
                best = None
                for base in (20., 35., 50., 65., 80., 95., 110.):
                    flexes[finger] = [base, min(base * 1.3, 120.), base]
                    curl(finger, hand_forward, palm)
                    depth_ = float(plate_depth(PP.world_points(skin)[chain]).max())
                    if best is None or depth_ < best[0]:
                        best = (depth_, list(flexes[finger]))
                flexes[finger] = best[1]
                curl(finger, hand_forward, palm)
            # Thumb arches over the rim; its pad settles onto the top surface.
            aim = centre + d * THUMB_R + n * (profile(PLATE_TOP, THUMB_R) + .009)
            for _ in range(80):
                t1 = arm.matrix_world @ named(arm, 'LeftHandThumb1').head
                orient_bone(arm, named(arm, 'LeftHandThumb1'), ((aim + n * .07) - t1).normalized())
                for joint, lift in ((2, -.01), (3, 0.)):     # the middle joint arches over the rim lip
                    bone = named(arm, 'LeftHandThumb' + str(joint))
                    orient_bone(arm, bone, ((aim + n * lift) - arm.matrix_world @ bone.head).normalized())
                points = PP.world_points(skin)
                tp, tr, th = pads(points, 'LeftHandThumb3', top=False)
                gap = th - profile(PLATE_TOP, tr)
                if abs(gap - .0005) < .0008 and abs(tr - THUMB_R) < .004:
                    break
                step = -n * (gap - .0005) + d * (THUMB_R - tr)
                if step.length > .003:
                    step = step.normalized() * .003
                aim = aim + step
            _, hand_forward, radial, _ = seated.palm(1)
            inverse = plate_matrix.inverted()
            grip_cache.update(wrist=inverse @ (arm.matrix_world @ left.hand.head), forward=inverse.to_3x3() @ hand_forward,
                              across=inverse.to_3x3() @ radial, digits={b.name: b.matrix_basis.copy() for b in hand_bones},
                              iterations=iteration + 1)
        else:
            rotation = plate_matrix.to_3x3()
            # Repeat the solve as the target frame's loop does, so the arm settles into the same shoulder and forearm roll.
            for _ in range(grip_cache['iterations']):
                check = left.pose(plate_matrix @ grip_cache['wrist'], rotation @ grip_cache['forward'], rotation @ grip_cache['across'],
                                  1, frame, pole=PLATE_POLE)
                check['distributed_palm_roll_degrees'] = PP.distribute_palm_roll(arm, left)
            for b in hand_bones:
                b.matrix_basis = grip_cache['digits'][b.name].copy()
            bpy.context.view_layer.update()
            points = PP.world_points(skin)
            tp, tr, th = pads(points, 'LeftHandThumb3', top=False)
            gap = th - profile(PLATE_TOP, tr)
        # Per-frame clearance: no skin inside the plate (depth into the plate body, metres).
        depth = plate_depth(points)
        f_pads = [pads(points, b) for b in ['LeftHandIndex3', 'LeftHandMiddle3']]
        plate.keyframe_insert('location', frame=frame)
        plate.keyframe_insert('rotation_euler', frame=frame)
        band = rows(rim(centre, tilt))
        _elbow = arm.matrix_world @ left.fore.head
        _wrist, _hand_forward, _, _ = seated.palm(1)
        check['wrist_bend_deg'] = math.degrees((_wrist - _elbow).angle(_hand_forward))
        check['grip_side_deg'] = GRIP_SIDE
        check.update(kind='plate_waiter', tilt_deg=tilt, turn_deg=PLATE_TURN * g, plate_scale=PLATE_SCALE,
                     chin_bottom_row=plate_choice['band'][4], plate_centre=list(centre),
                     max_skin_depth_into_plate_m=float(depth.max()),
                     max_hand_depth_into_plate_m=float(depth[verts].max()),
                     deepest_bone=seated.dominant[int(depth.argmax())],
                     index_pad_gap_m=float(profile(PLATE_UNDER, f_pads[0][1]) - f_pads[0][2]),
                     index_tip_clearance_m=-float(plate_depth(points[names['LeftHandIndex3']]).max()),
                     middle_tip_clearance_m=-float(plate_depth(points[names['LeftHandMiddle3']]).max()),
                     thumb_tip_clearance_m=-float(plate_depth(points[names['LeftHandThumb3']]).max()),
                     middle_pad_gap_m=float(profile(PLATE_UNDER, f_pads[1][1]) - f_pads[1][2]),
                     index_pad_radius_m=f_pads[0][1], middle_pad_radius_m=f_pads[1][1],
                     thumb_pad_gap_m=float(gap), thumb_pad_radius_m=tr,
                     plate_rows_from_top=[min(y for y, _ in band), max(y for y, _ in band)],
                     plate_columns=[min(x for _, x in band), max(x for _, x in band)])
        return check

    if spec.get('low_elbow'):
        # The gap is measured with the head where it meets the fork, at the full lean; the margin covers the
        # 0.5 mm the clamped-wrist solve may land short of its target.
        seated.body(position, spec['look'], lean=BITE_LEAN)
        aim_at_lips(.0005)

    held = prop or (plate if act == 'plate' else None)
    solved = {}

    def action(u):
        frame = bpy.context.scene.frame_current
        nod = 2 * math.sin(math.pi * P.smooth((u - .62) / .3)) ** 2 if act in ('gesture', 'plate') or spec.get('nod') else 0.
        if act in ('sip', 'bite'):
            amount = P.smooth((u - .12) / .35) * (1 - P.smooth((u - .72) / .22))
        else:
            amount = P.smooth((u - .10) / .32) * (1 - P.smooth((u - .64) / .30)) if act else 0.
        # A repeated pose (the target opens and closes the guide) restores the first solve bit for bit.
        key = (round(amount, 9), round(nod, 9))
        if key in solved:
            bones, transform, check = solved[key]
            for bone in arm.pose.bones:
                bone.matrix_basis = bones[bone.name].copy()
            if held:
                held.location, held.rotation_euler = transform[0].copy(), transform[1].copy()
                held.keyframe_insert('location', frame=frame)
                held.keyframe_insert('rotation_euler', frame=frame)
            bpy.context.view_layer.update()
            seated.key(frame)
            state['performance_checks'].append(dict(u=u, frame=frame, seated=check, arms=check['arms'], repeated=True))
            return
        check = seated.body(position, spec['look'], nod, BITE_LEAN * amount if spec.get('low_elbow') else 0.)
        arms = [seated.lap_hand(frame) if front else seated.rest_hand(-1, frame)]
        if act in ('sip', 'bite'):
            arms.append(hold_prop(u, frame))
        elif act == 'gesture':
            arms.append(gesture(u, frame))
        elif act == 'plate':
            arms.append(hold_plate(u, frame))
        else:
            arms.append(seated.rest_hand(1, frame))
        seated.key(frame)
        check.update(measured, arms=arms, eye_after_pose=list(seated.eye()))
        check.update(contact_report(skin, region, Vector((0, chair_y, 0)), table_centre))
        solved[key] = ({bone.name: bone.matrix_basis.copy() for bone in arm.pose.bones},
                       (held.location.copy(), held.rotation_euler.copy()) if held else None, check)
        state['performance_checks'].append(dict(u=u, frame=frame, seated=check, arms=arms))

    state['actions'] = [action]
    state['contacts'] = [dict(kind='canonical_character', source='model_refferences/creator/lineart/asset.blend',
                              skeleton_preserved=True, anatomical_hands=2, facial_animation=False, pose='seated'),
                         dict(kind='camera_mode', camera=record['camera'], preview_mirrored=front)]
    state['adaptations'] = [
        'Seated canonical creator: hips on the dining chair seat, knees under the table; the right hand rests on the table (in her lap for selfies).',
        'Protected face is the eye line to the chin, so the eyes sit one third from the top inside the P0 band.',
        f'{state["lens_mm"]} mm lens ({"front camera" if front else "rear 1x"}); character fade floor {FADE_FLOOR:.3f} m.',
        'Cup and fork use the grips approved in the published sip and bite guides; the open palm is the approved verdict gesture.']
    if spec.get('grip') == 'tripod':
        state['adaptations'].append('Fork in a pencil hold, tines up (fork_grip.md): handle on the middle finger, index pad on top, thumb pad on '
                                    'the palm-side edge, ring and little finger curled; the handle end rests over the thumb web.')
    return dict(state, target_position=position, target_aim=target, sample=lambda u, p, t: (p, t))
