import cadquery as cq

# Axes: X along the table edge, Y from inside the table towards its edge,
# Z up.
# The top surface of the table is Z = 0, the table edge is Y = 0.

# --- Inputs (mm) ---
table_thickness = 25
cable_dia = 5
cable_count = 2

# --- Constants ---
width = 20             # width of the clip along the table edge
wall = 3               # wall thickness
jaw_length = 30        # how far the jaws reach under/over the table
squeeze = 0.5          # jaw gap is this much narrower than the table
channel_allowance = 1.0  # channel diameter exceeds the cable by this much
entry_narrowing = 1.5  # entry slot is this much narrower than the channel
block_length = 15      # length of the cable block in the Y direction
corner_radius = 2      # fillet at the inner corners of the jaws
edge_gap = corner_radius   # the spine stands this far off the table edge
entry_chamfer = 1.5    # chamfer at the tip of the lower jaw

# --- Derived dimensions ---
jaw_gap = table_thickness - squeeze
channel_dia = cable_dia + channel_allowance
entry_width = channel_dia - entry_narrowing
block_height = channel_dia + 4
channel_z = wall + block_height / 2
channel_pitch = width / cable_count

# --- Step 1: body (the side-view profile is extruded) ---
top = wall + block_height
spine_in = edge_gap            # face of the spine towards the table
spine_out = edge_gap + wall    # outer face of the spine
profile = [
    (-jaw_length, 0), (spine_in, 0), (spine_in, -jaw_gap),
    (-jaw_length, -jaw_gap), (-jaw_length, -jaw_gap - wall),
    (spine_out, -jaw_gap - wall), (spine_out, top),
    (spine_out - block_length, top), (spine_out - block_length, wall),
    (-jaw_length, wall),
]
clip = (
    cq.Workplane("YZ").polyline(profile).close()
    .extrude(width / 2, both=True)
)

# --- Step 2: cable channels and their entry slots from above ---
centres = [((i + 0.5) * channel_pitch - width / 2, channel_z)
           for i in range(cable_count)]
# A workplane on the outer face of the spine
outer_face = cq.Workplane("XZ").workplane(offset=-spine_out)
channels = (
    outer_face.pushPoints(centres).circle(channel_dia / 2).extrude(block_length)
)
entry_h = top - channel_z + 1
entries = (
    outer_face.pushPoints([(x, z + entry_h / 2) for x, z in centres])
    .rect(entry_width, entry_h).extrude(block_length)
)
clip = clip.cut(channels).cut(entries)

# --- Step 3: inner corner fillets (2 edges), chamfer on the jaw tip (1 edge) ---
inner_corners = (
    cq.selectors.BoxSelector((-width, spine_in - 1, -1),
                             (width, spine_in + 1, 1))
    + cq.selectors.BoxSelector((-width, spine_in - 1, -jaw_gap - 1),
                               (width, spine_in + 1, -jaw_gap + 1))
)
clip = clip.edges(inner_corners).fillet(corner_radius)
jaw_tip = cq.selectors.BoxSelector(
    (-width, -jaw_length - 1, -jaw_gap - 1),
    (width, -jaw_length + 1, -jaw_gap + 1),
)
clip = clip.edges(jaw_tip).chamfer(entry_chamfer)

# --- Measure and save ---
b = clip.val().BoundingBox()
print("outer size:", round(b.xlen, 2), round(b.ylen, 2), round(b.zlen, 2))
print("volume:", round(clip.val().Volume()))
print("solids:", len(clip.solids().vals()),
      "valid:", clip.val().isValid())
print("jaw gap:", jaw_gap, "channel dia:", channel_dia,
      "entry width:", entry_width)

cq.exporters.export(clip, "cable_clip.step")
cq.exporters.export(clip, "cable_clip.stl",
                    tolerance=0.05, angularTolerance=0.2)
