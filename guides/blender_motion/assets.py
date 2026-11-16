"""Reusable three-dimensional subjects for the filming-guide rollout."""
import math
import bpy
from mathutils import Vector
import geometry as G


def empty(name, position=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = position
    return obj


def tag(obj, role, reason):
    obj["composition_role"] = role
    obj["placement_reason"] = reason
    return obj


def group(name, before, position=(0, 0, 0), role="support", reason="Relevant supporting subject"):
    root = empty(name)
    for obj in set(bpy.data.objects) - before - {root}:
        if obj.parent is None:
            obj.parent = root
        if obj.type == "MESH" and "composition_role" not in obj:
            tag(obj, role, reason)
    root.location = position
    return root


def ellipsoid(name, position, radii, role="support", reason="Recognizable curved volume"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=position)
    obj = G.finish(bpy.context.object, name)
    obj.scale = radii
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for face in obj.data.polygons:
        face.use_smooth = True
    return tag(obj, role, reason)


def table(position=(0, 0, 0), radius=.60):
    before = set(bpy.data.objects)
    G.lathe("Quiet tabletop", [(0, .75), (radius, .75), (radius, .777),
                                (radius-.02, .785), (0, .785)], (0, 0, 0), 64)
    return group("Reusable table", before, position, "structure", "A stable support; its edge adds depth without competing")


def plate(position=(0, 0, .785), role="support"):
    obj = G.lathe("Plate with formed rim", [(0, 0), (.09, 0), (.13, .012), (.15, .022),
                   (.151, .029), (.139, .030), (.115, .015), (.09, .009), (0, .009)], position, 64)
    return tag(obj, role, "Frames the food with clear rim separation and a real supporting base")


def cup(position=(0, 0, .795), name="Cup", role="hero"):
    before = set(bpy.data.objects)
    G.lathe(name + " hollow ceramic body", [(0, 0), (.035, 0), (.041, .007), (.054, .085),
        (.053, .118), (.048, .118), (.047, .085), (.035, .017), (0, .017)], (0, 0, 0), 64)
    points = [(.047, 0, .094), (.081, .003, .096), (.099, .004, .066),
              (.081, .003, .037), (.049, 0, .037)]
    G.tube(name + " open handle", points, .006)
    G.lathe(name + " coffee surface", [(0, .106), (.045, .106)], (0, 0, 0), 48)
    return group(name, before, position, role, "The drink is the shot subject; the asymmetric handle reveals real viewpoint change")


def saucer(position=(0, 0, .785)):
    return tag(G.lathe("Saucer", [(0, 0), (.07, 0), (.085, .007), (.088, .012),
             (.080, .017), (.048, .010), (0, .010)], position, 48), "support", "Grounds the cup and establishes scale")


def fork(position=(0, 0, 0), name="Fork", role="support"):
    # Table fork, length 0.19: rounded handle end, slim neck, a head with four parallel tines along +Y.
    before = set(bpy.data.objects)
    side = [(.0095, -.128), (.0105, -.112), (.0085, -.06), (.0040, -.005), (.0045, .008), (.0105, .022), (.0110, .030)]
    tine, gap = .0034, .0018
    tines = []
    for k in range(4):
        left = -(4 * tine + 3 * gap) / 2 + k * (tine + gap)
        if k:
            tines += [(left - gap, .036), (left - gap / 2, .033), (left, .036)]
        tines += [(left, .060), (left + tine / 2, .062), (left + tine, .060)]
    outline = [(-x, y) for x, y in side] + tines + [(x, y) for x, y in reversed(side)]
    outline += [(.0095 * math.cos(a), -.128 - .0095 * math.sin(a)) for a in [i * math.pi / 6 for i in range(1, 6)]]

    def lift(x, y):
        return .010 * max(0, (y - .015) / .047) ** 2 + .006 * max(0, (-.07 - y) / .058) ** 2

    G.plate_outline(name + " stamped body", outline, .0022, lift)
    return group(name, before, position, role, "The utensil has a purpose and points into the food/action")


def knife(position=(0, 0, 0), name="Dinner knife", role="support", length=None):
    # Dinner knife, length 0.236 along +Y: rounded handle, bolster, blade with a straight spine (+X), a slight belly
    # on the cutting edge (-X) and a rounded tip. Rests on the surface at the given position. `length` (for example
    # 0.20 for a dessert knife) scales the whole knife uniformly.
    if length is not None:
        root = knife((0, 0, 0), name, role)
        root.scale = (length / .236,) * 3
        root.location = position
        return root
    before = set(bpy.data.objects)
    blade = [(.0085, -.005), (.0088, .03), (.0088, .07), (.0083, .095), (.0068, .108), (.0042, .116), (.0010, .1195),
             (-.0025, .119), (-.0060, .115), (-.0088, .106), (-.0103, .090), (-.0108, .065), (-.0102, .035),
             (-.0090, .010), (-.0085, -.005)]
    G.plate_outline(name + " blade", blade, .002).location.z = .0012
    bolster = [(-.0060, -.017), (.0060, -.017), (.0070, -.010), (.0086, -.004), (-.0086, -.004), (-.0070, -.010)]
    G.plate_outline(name + " bolster", bolster, .0065).location.z = .0033
    handle = [(-.0062, -.015), (.0062, -.015), (.0072, -.05), (.0082, -.09), (.0084, -.108)]
    handle += [(.0084 * math.cos(a), -.108 - .0084 * math.sin(a)) for a in [i * math.pi / 8 for i in range(1, 8)]]
    handle += [(-.0084, -.108), (-.0082, -.09), (-.0072, -.05)]
    G.plate_outline(name + " handle", handle, .008).location.z = .0040
    return group(name, before, position, role, "Place-setting knife beside the plate, edge toward the plate")


def spoon(position=(0, 0, 0), name="Dessert spoon", role="support", length=.175):
    # Spoon along +Y: a shallow oval bowl (wider toward the tip) on a slim stamped handle with a rounded end that
    # lifts slightly off the table, as the fork does. 0.175 m is a dessert spoon; 0.135 m a teaspoon.
    before = set(bpy.data.objects)
    s = length / .175
    bowl_r, stretch, bowl_y = .0195, 1.38, .034
    profile = [(0, .0016), (bowl_r * .55, .0022), (bowl_r * .85, .0042), (bowl_r, .0068), (bowl_r * .97, .0080),
               (bowl_r * .82, .0060), (bowl_r * .45, .0036), (0, .0030)]
    bowl = G.lathe(name + " bowl", profile, (0, bowl_y, 0), 40, stretch)
    neck_y = bowl_y - bowl_r * stretch + .002
    side = [(.0028, neck_y), (.0034, neck_y - .012), (.0058, -.050), (.0080, -.098), (.0084, -.112)]
    outline = [(x, y) for x, y in side] + [(.0084 * math.cos(a), -.112 - .0084 * math.sin(a)) for a in
                                           [i * math.pi / 6 for i in range(1, 6)]] + [(-x, y) for x, y in reversed(side)]

    def lift(x, y):
        return .0020 + .006 * max(0, (-.07 - y) / .05) ** 2

    G.plate_outline(name + " handle", outline, .0024, lift)
    root = group(name, before, (0, 0, 0), role, "The utensil has a purpose and points into the food/action")
    root.scale = (s, s, s)
    root.location = position
    return root


def paper_wrap(position=(0, 0, 0), opened=False, name="Paper wrap", role="hero"):
    # A generic wrapped handheld (burger, sandwich), about 0.12 m across. Closed: a soft paper parcel with a folded
    # top flap. Opened: the paper folded down into a sleeve around the lower half, the bun and filling showing.
    before = set(bpy.data.objects)
    if not opened:
        tag(G.block(name + " parcel", (0, 0, .032), (.125, .105, .064), .012), role, "Wrapped handheld parcel")
        flap = [(-.046, .036), (.046, .036), (.032, .000), (0, -.016), (-.032, .000)]
        tag(G.plate_outline(name + " top flap", flap, .0012, lambda x, y: .0646), role,
            "The folded paper flap reads the parcel as wrapped")
    else:
        sleeve = [(.050, 0), (.056, .002), (.060, .040), (.0615, .046), (.0595, .046), (.0585, .040), (.054, .004), (0, .004)]
        tag(G.lathe(name + " sleeve", sleeve, (0, 0, 0), 48, .92), role, "Paper sleeve holds the handheld")
        tag(G.lathe(name + " filling", [(0, .046), (.062, .046), (.066, .051), (.062, .056), (0, .056)], (0, 0, 0), 48, .92),
            role, "A filling layer that overhangs the paper rim a little")
        ellipsoid(name + " bun", (0, 0, .060), (.055, .0505, .028), role, "Top bun dome")
    return group(name, before, position, role, "Generic handheld in its paper")


def paper_tray(position=(0, 0, 0), name="Paper-lined tray", role="support", size=(.36, .27)):
    # A shallow fast-food tray (0.36 x 0.27 m, 0.02 m deep) with a paper liner lying slightly askew inside.
    before = set(bpy.data.objects)
    w, d = size
    tag(G.block(name + " base", (0, 0, .002), (w, d, .004), .002), role, "Tray base")
    rim = .012
    for x, y, sx, sy in ((0, d / 2 - rim / 2, w, rim), (0, -d / 2 + rim / 2, w, rim),
                         (w / 2 - rim / 2, 0, rim, d - 2 * rim), (-w / 2 + rim / 2, 0, rim, d - 2 * rim)):
        tag(G.block(name + " rim", (x, y, .010), (sx, sy, .020), .004), role, "Tray rim")
    lw, ld, turn = w - .06, d - .055, math.radians(4)
    corners = [(-lw / 2, -ld / 2), (lw / 2, -ld / 2), (lw / 2, ld / 2), (-lw / 2, ld / 2)]
    liner = [(x * math.cos(turn) - y * math.sin(turn), x * math.sin(turn) + y * math.cos(turn)) for x, y in corners]
    tag(G.plate_outline(name + " paper liner", liner, .0008, lambda x, y: .0048), "background", "Paper liner, slightly askew")
    return group(name, before, position, role, "Tray the handheld is served on")


def product_box(position=(0, 0, 0), w=.152, d=.102, h=.051, flap=True, name="Product box", role="hero"):
    # A generic unlabelled retail box (default 6 x 4 x 2 in). flap=True: a telescoping lid 2 mm proud of the body on
    # every side, so its lower edge draws a seam line and the box does not read as a plain block.
    before = set(bpy.data.objects)
    if flap:
        lid = max(.012, h * .3)
        tag(G.block(name + " body", (0, 0, (h - lid * .5) / 2), (w, d, h - lid * .5), .002), role, "Box body")
        tag(G.block(name + " lid", (0, 0, h - lid / 2), (w + .004, d + .004, lid), .002), role,
            "Lid overhang draws the seam that reads it as a box")
    else:
        tag(G.block(name, (0, 0, h / 2), (w, d, h), .002), role, "Plain box")
    return group(name, before, position, role, "Generic product on a shelf or in the hand")


def shopping_bag(position=(0, 0, 0), w=.254, d=.152, h=.330, name="Shopping bag", role="hero"):
    # A generic paper shopping bag (default 10 x 6 x 13 in): front and back panels, side gussets folded in (a V seen
    # from above), a folded top cuff and two twisted-rope handles. No print or logo.
    before = set(bpy.data.objects)
    t, cuff, g = .0015, .035, .028
    for sy in (1, -1):
        tag(G.block(name + " panel", (0, sy * d / 2, h / 2), (w, t, h), .001), role, "Front or back panel")
        tag(G.block(name + " cuff", (0, sy * (d / 2 + .002), h - cuff / 2), (w + .002, t + .004, cuff), .001), role,
            "Folded top cuff")
        tag(G.tube(name + " handle", [(-.05, sy * d / 2, h - .012), (-.045, sy * d / 2, h + .07), (0, sy * d / 2, h + .095),
                                      (.045, sy * d / 2, h + .07), (.05, sy * d / 2, h - .012)], .0035), role, "Rope handle")
    half = math.hypot(d / 2, g)
    angle = math.atan2(g, d / 2)
    for sx in (1, -1):
        for sy in (1, -1):
            side = G.block(name + " gusset", (sx * (w / 2 - g / 2), sy * d / 4, h / 2), (t, half, h), .001)
            side.rotation_euler = (0, 0, -sx * sy * angle)
            tag(side, role, "Side gusset folded in")
    tag(G.block(name + " base", (0, 0, t / 2), (w, d, t), .001), role, "Bag base")
    return group(name, before, position, role, "Generic shopping bag at checkout")


def pasta(position=(0, 0, .785)):
    before = set(bpy.data.objects)
    plate((0, 0, 0))
    noodles=[]
    for j in range(9):
        points = []
        for k in range(40):
            t = k / 39 * 2 * math.pi
            r = .027 + .006 * (j % 3)
            points.append((.043*math.cos(j*2.4)+r*math.cos(t),
                           .032*math.sin(j*2.4)+r*math.sin(t),
                           .023+.005*j+.006*math.sin(t*2+j)))
        noodles.append(tag(G.tube("Pasta coil", points, .004), "hero", "A compact noodle mound gives the orbit readable near/far structure"))
    bottom=min(v.co.z for obj in noodles for v in obj.data.vertices)
    for obj in noodles:obj.location.z=.009-bottom
    near=[v.co.z+obj.location.z for obj in noodles for v in obj.data.vertices if math.hypot(v.co.x-.025,v.co.y+.01)<.018]
    leaf = ellipsoid("Basil leaf", (.025, -.01, max(near)+.0025), (.021, .010, .0025), "support", "A small asymmetric food accent rests on the noodle mound")
    leaf.rotation_euler.z=.5
    return group("Pasta plate", before, position)


def pastry(position=(0, 0, .794)):
    before = set(bpy.data.objects)
    halves = []
    for side in range(2):
        vertices, faces = [], []
        for j in range(21):
            u = (side * 20 + j) / 40
            angle = .12*math.pi + u*.76*math.pi
            centre = Vector((.105*math.cos(angle), .072*math.sin(angle), .018))
            radius = .012 + .022 * math.sin(math.pi*u)
            for k in range(16):
                v = k / 16 * 2 * math.pi
                vertices.append(tuple(centre + Vector((math.cos(angle)*radius*math.cos(v),
                    math.sin(angle)*radius*math.cos(v), radius*.8*math.sin(v)))))
        for j in range(20):
            for k in range(16):
                a=j*16+k; n=j*16+(k+1)%16
                faces.append((a,n,n+16,a+16))
        faces += [tuple(reversed(range(16))), tuple(range(20*16,21*16))]
        mesh=bpy.data.meshes.new("Croissant half mesh");mesh.from_pydata(vertices, [], faces);mesh.update()
        obj=bpy.data.objects.new("Croissant half",mesh);bpy.context.collection.objects.link(obj);G.finish(obj,obj.name)
        for face in mesh.polygons: face.use_smooth=True
        root=empty("Pastry half rig");obj.parent=root;halves.append(root)
        # Raised laminated seams make the curved pastry readable at phone size.
        for seam in range(1,6):
            u=(side*20+seam*3)/40
            angle=.12*math.pi+u*.76*math.pi
            centre=Vector((.105*math.cos(angle),.072*math.sin(angle),.018))
            radius=.012+.022*math.sin(math.pi*u)
            points=[centre+Vector((math.cos(angle)*radius*math.cos(v),math.sin(angle)*radius*math.cos(v),radius*.8*math.sin(v))) for v in [j*math.pi/12 for j in range(13)]]
            ridge=G.tube("Laminated pastry seam",points,.0011);ridge.parent=root

    meshes=[obj for obj in set(bpy.data.objects)-before if obj.type=="MESH"]
    bottom=min(v.co.z for obj in meshes for v in obj.data.vertices)
    for obj in meshes:
        for vertex in obj.data.vertices:vertex.co.z-=bottom
    root=group("Reusable croissant",before,position,"hero","A curved pastry with a real resting base and two consistent halves")
    return root, halves


def hand(position=(0, 0, 0), scale=1, mirror=1, pose="pinch"):
    """One life-size anatomical CC0 hand gripping at this frame's grip point: fingers along +Z, palm facing -Y."""
    import real_hands
    frame = empty("One hand", (0, 0, 0))
    grip = real_hands.place(pose, "L" if mirror < 0 else "R", target=(.01 * mirror, -.032, .026),
                            forward=(0, 0, 1), normal=(0, -1, 0), anchor="grip")
    grip.parent = frame
    frame.location = position
    frame["visible_hand_count"] = 1
    frame["hand_source"] = "para / MakeHuman CC0"
    return frame


def menu_board(position=(0, .7, 1.90), flat=False, title="SEASONAL DRINK", selected="HOUSE LATTE", right="PRICE", rows=None, tall=False):
    before=set(bpy.data.objects)
    height=1.04 if tall else .52
    G.block("Menu board backing", (0, 0, 0), (.64, .025, height), .009)
    for xx in [-.32,.32]: G.block("Menu frame side",(xx,-.020,0),(.017,.018,height+.02),.003)
    for zz in [-height/2,height/2]: G.block("Menu frame rail",(0,-.020,zz),(.65,.018,.017),.003)
    # The name/price columns divide close to the golden-ratio point of the board.
    lettering=[(title,-.27,.16,.040),(selected,-.20,.055,.028),(right,.10,.055,.030)] if rows is not None else [(title,-.27,.16,.044),(selected,-.25,.055,.032),(right,.10,.055,.032)]
    if tall:
        lettering=[(title,-.27,.40,.040),(selected,-.15,.055,.028),(right,.09,.055,.025)]
    if rows is not None:
        for index,(left,value) in enumerate(rows):
            z=-.18-index*.10 if tall else -.04-index*.09
            lettering.extend([(left,-.15 if tall else -.20,z,.028),(value,.09 if tall else .10,z,.025)])
    for text,x,z,size in lettering:
        data=bpy.data.curves.new("Menu resource lettering", "FONT");data.body=text;data.size=size;data.extrude=.0001
        obj=bpy.data.objects.new("Menu resource lettering",data);bpy.context.collection.objects.link(obj)
        obj.location=(x,-.020,z);obj.rotation_euler.x=math.pi/2
        bpy.ops.object.select_all(action="DESELECT");obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.ops.object.convert(target="MESH");G.finish(bpy.context.object,obj.name)
        tag(obj,"hero","Resource text identifies the name and price areas without inventing venue pricing")
    for zz in ([] if rows is not None else [-.04,-.13]):
        G.tube("Quiet menu row",[(-.26,-.022,zz),(.06,-.022,zz)],.0015)
        G.tube("Quiet menu price field",[(.16,-.022,zz),(.25,-.022,zz)],.0015)
    root=group("Reusable menu",before,position,"support","A legible resource board with a chosen name/price line and quiet surrounding rows")
    if flat: root.rotation_euler.x=-math.pi/2
    return root


def fixed_side_light(target=(0,0,.85),warm=True):
    """A broad steady window/fixture source; no time-of-day sweep or bloom."""
    data=bpy.data.lights.new("Fixed broad side light","AREA");data.energy=55;data.shape="DISK";data.size=.65
    data.color=(1,.90,.76) if warm else (.93,.96,1)
    obj=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(obj)
    obj.location=Vector(target)+Vector((-.65,-.18,.55))
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    obj["purpose"]="Steady side light reveals curved form; creator positions camera within existing light"
    return obj


def studio_sign(position=(-.43,.35,1.93)):
    before=set(bpy.data.objects)
    G.block("Studio sign backing",(0,0,0),(.20,.022,.09),.004)
    text=bpy.data.curves.new("Studio resource name","FONT");text.body="STUDIO";text.size=.030;text.extrude=.0001
    obj=bpy.data.objects.new("Studio resource name",text);bpy.context.collection.objects.link(obj)
    obj.location=(-.06,-.013,-.010);obj.rotation_euler.x=math.pi/2
    bpy.ops.object.select_all(action="DESELECT");obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target="MESH");G.finish(bpy.context.object,obj.name)
    return group("Studio sign",before,position,"important_background","The source explicitly reveals a studio sign; keep it clearer than incidental context")


def rim_light_cue(centre,radius,angle=None,span=65):
    if angle is None:angle=math.atan2(-.18,-.65)
    points=[(centre[0]+radius*math.cos(a),centre[1]+radius*math.sin(a),centre[2])
            for a in [angle+math.radians(-span/2+j*span/24) for j in range(25)]]
    return tag(G.tube("Window-facing rim highlight",points,.00045),"lighting_cue",
               "A restrained warm rim cue stays attached to the real light-facing surface")


def portrait(position=(8, 0, 0), prop="cup"):
    before=set(bpy.data.objects)
    torso=G.lathe("Schematic torso",[(0,.96),(.15,.96),(.17,1.12),(.22,1.34),(.19,1.39),(.06,1.43),(0,1.43)],(0,0,0),48,ellipse=.52)
    tag(torso,"support","Quiet shoulders provide human context below the face")
    G.lathe("Neck",[(.045,1.36),(.045,1.49)],(0,0,0),32,ellipse=.85)
    head=G.lathe("Mouthless schematic head",[(0,1.44),(.036,1.445),(.072,1.49),(.093,1.57),
          (.095,1.66),(.077,1.745),(.037,1.78),(0,1.79)],(0,0,0),48,ellipse=.82)
    for vertex in head.data.vertices:
        if vertex.co.y < 0:
            vertex.co.y -= .025 * math.exp(-((vertex.co.x/.025)**2+((vertex.co.z-1.605)/.027)**2))
    tag(head,"hero","Face stays schematic and mouthless, with clean headroom and separation")
    for side in [-1,1]: ellipsoid("Ear",(side*.094,0,1.61),(.014,.012,.030))
    if prop is None:
        root=group("Reusable creator bust",before,position,"support","Quiet mouthless portrait; no unnecessary hands or props")
        return dict(root=root,grip=None,arm=[],prop=None)
    grip=empty("Resource grip",(.16,-.20,1.22))
    held_hand=hand();held_hand.parent=grip
    if prop=="cup":
        held=cup((-.06,-.025,-.008),name="Held cup");held.parent=grip;held.scale=(.75,)*3
    elif prop=="fork":
        held=fork((-.02,-.025,.018),role="hero");held.parent=grip;held.rotation_euler.x=math.pi/2
    arm=[]
    for name,radius in [("Upper arm",.035),("Forearm",.026)]:
        arm.append(G.lathe(name,[(0,0),(radius,0),(radius,1),(0,1)],(0,0,0),24))
    root=group("Reusable creator bust",before,position,"support","Mouthless human context with only one visible hand")
    root["visible_hand_count"]=1
    return dict(root=root,grip=grip,arm=arm,prop=prop)


def pose_portrait(actor, frame, amount, wrist_position=None):
    grip=actor["grip"];grip.location=(.16,-.20+.13*amount,1.22+.20*amount)
    if wrist_position is not None:grip.location=wrist_position
    grip.rotation_euler.x=math.radians(-12*amount)
    grip.keyframe_insert(data_path="location",frame=frame);grip.keyframe_insert(data_path="rotation_euler",frame=frame)
    shoulder=Vector((.19,0,1.35));wrist=Vector(grip.location)
    axis=(wrist-shoulder).normalized();distance=(wrist-shoulder).length
    along=(.28**2-.26**2+distance**2)/(2*distance)
    drop=Vector((0,0,-1));drop=(drop-axis*drop.dot(axis)).normalized()
    elbow=shoulder+axis*along+drop*math.sqrt(max(0,.28**2-along**2))
    for obj,a,b in zip(actor["arm"],[shoulder,elbow],[elbow,wrist]):
        obj.location=a;obj.rotation_mode="QUATERNION";obj.rotation_quaternion=(b-a).to_track_quat("Z","Y")
        obj.scale=(1,1,(b-a).length)
        for path in ["location","rotation_quaternion","scale"]: obj.keyframe_insert(data_path=path,frame=frame)
