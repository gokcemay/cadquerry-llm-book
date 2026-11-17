import cadquery as cq

# --- Workplane and sketch ---
p = cq.Workplane("XY")                  # XY: extrudes towards Z. "XZ" goes towards -Y!
p = p.workplane(offset=5)               # move the plane 5 mm up
p = p.center(10, 0)                     # shift the origin (permanent)
p = p.rect(40, 20)                      # or .circle(r), .polygon(6, d)
p = cq.Workplane("XY").polyline([(0, 0), (30, 0), (0, 20)]).close()

# --- Making solids ---
box = cq.Workplane("XY").box(40, 30, 10)             # centred box
corner = cq.Workplane("XY").box(40, 30, 10, centered=False)
cyl = cq.Workplane("XY").circle(8).extrude(20)       # extrusion
both = cq.Workplane("XZ").rect(10, 4).extrude(15, both=True)   # both directions
spun = (cq.Workplane("XZ").polyline([(5, 0), (9, 0), (9, 12), (5, 12)])
        .close().revolve(360, (0, 0, 0), (0, 1, 0)))  # revolve

# --- Boolean operations ---
union = box.union(cyl)
difference = box.cut(cyl)
common = box.intersect(cyl)

# --- Selectors ---
top = box.faces(">Z")                   # the topmost face; "<Z" the lowest
vertical = box.edges("|Z")              # edges parallel to Z (4)
sides = box.faces("#Z")                 # faces whose normal is perpendicular to Z (4)
second = box.faces(">Z[-2]")            # second from the top
combined = box.edges("|Z and >Y")       # combine with and / or / not
region = box.edges(cq.selectors.BoxSelector((15, -20, -6), (25, 20, 6)))

# --- Modifying ---
filleted = box.edges("|Z").fillet(3)                 # fillet
chamfered = box.faces(">Z").edges().chamfer(1)       # chamfer
drilled = box.faces(">Z").workplane().hole(6)        # through hole
countersunk = (box.faces(">Z").workplane()
               .pushPoints([(-10, 0), (10, 0)]).cskHole(4.5, 9, 90))
hollow = box.faces(">Z").shell(-2)                   # open-topped shell
lettered = (box.faces(">Z").workplane()
            .text("AD", 8, 0.8, combine=True))       # combine is essential

# --- Repeating ---
grid = (box.faces(">Z").workplane()
        .rarray(12, 10, 3, 2).hole(3))               # 3 x 2 grid
circular = (cq.Workplane("XY").circle(20).extrude(4).faces(">Z").workplane()
            .polarArray(14, 0, 360, 6).hole(3))      # 6 on a circle
mirrored = corner.mirror("YZ", union=True)           # union is essential

# --- Tags ---
tagged = box.faces(">Z").tag("top").faces("<Z").workplane()
back = tagged.faces(tag="top")                       # return to the tagged state

# --- Measuring ---
s = countersunk.val()
b = s.BoundingBox()
print("outer size:", b.xlen, b.ylen, b.zlen)
print("volume:", round(s.Volume()), "| valid:", s.isValid())
print("solids:", countersunk.solids().size(),
      "| cone faces:", countersunk.faces("%CONE").size())
overlap = box.intersect(cyl)
print("overlap volume:", round(overlap.val().Volume(), 1))

# --- Assembly ---
assembly = cq.Assembly()
assembly.add(box, name="box", color=cq.Color(0.9, 0.8, 0.3))
assembly.add(cyl, name="pin", loc=cq.Location((0, 0, 10)))

# --- Exporting ---
cq.exporters.export(countersunk, "part.step")
cq.exporters.export(countersunk, "part.stl", tolerance=0.05,
                    angularTolerance=0.2)
cq.exporters.exportDXF(box.section(), "part.dxf")     # mind the section height!
assembly.export("assembly.step")
back_read = cq.importers.importStep("part.step")
