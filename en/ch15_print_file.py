import cadquery as cq

# Rotates the headphone hanger to the chosen print orientation and sits it on
# the bed. The slicer then opens the file in the right orientation.

hanger = cq.importers.importStep("headphone_hanger.step")

# Rotate so that the X axis points up: the profile lies flat on the bed
lying = hanger.rotate((0, 0, 0), (0, 1, 0), -90)

# Sit it on the bed: lowest point at Z = 0
low = lying.val().BoundingBox().zmin
lying = lying.translate((0, 0, -low))

b = lying.val().BoundingBox()
print("print size:", round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1))
print("lowest point:", round(b.zmin, 3))

cq.exporters.export(lying, "headphone_hanger_print.stl",
                    tolerance=0.05, angularTolerance=0.2)
