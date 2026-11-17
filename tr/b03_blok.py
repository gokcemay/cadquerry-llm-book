import cadquery as cq

blok = (
    cq.Workplane("XY")
    .box(40, 30, 10)                      # 40 x 30 x 10 mm blok
    .edges("|Z").fillet(3)                # dört dik kenara 3 mm kavis
    .faces(">Z").workplane().hole(8)      # üst yüzden 8 mm çaplı delik
)

cq.exporters.export(blok, "blok.step")
