import math
import cadquery as cq

PLA_DENSITY = 1.24        # g/cm3


def make_stand(device_width, device_height, device_thickness, angle=65,
               clearance=1.5):
    """The stand from Chapter 8; also returns the derived dimensions."""
    wall = 4
    front_margin = 10
    rear_margin = 15

    d = {"wall": wall, "angle": angle}
    d["width"] = round(0.9 * device_width)
    d["back_length"] = round(0.6 * device_height)
    d["lip_height"] = max(10, device_thickness + 3)
    d["slot"] = (device_thickness + clearance) / math.sin(math.radians(angle))
    d["lip_x"] = front_margin
    d["back_x"] = d["lip_x"] + wall + d["slot"]
    projection = d["back_length"] * math.cos(math.radians(angle))
    d["base_depth"] = d["back_x"] + projection + rear_margin

    base = cq.Workplane("XY").box(
        d["base_depth"], d["width"], wall, centered=(False, True, False)
    )
    back = (
        cq.Workplane("XY")
        .box(wall, d["width"], d["back_length"], centered=(False, True, False))
        .rotate((0, 0, 0), (0, 1, 0), 90 - angle)
        .translate((d["back_x"], 0, wall))
    )
    lip = (
        cq.Workplane("XY")
        .box(wall, d["width"], wall + d["lip_height"],
             centered=(False, True, False))
        .translate((d["lip_x"], 0, 0))
    )
    return base.union(back).union(lip), d


def device_model(d, width, height, thickness):
    """A block modelling the device leaning on the backrest and resting on the base."""
    return (
        cq.Workplane("XY")
        .box(thickness, width, height, centered=(False, True, False))
        .translate((-thickness, 0, 0))
        .rotate((0, 0, 0), (0, 1, 0), 90 - d["angle"])
        .translate((d["back_x"], 0, d["wall"]))
    )


def common_volume(a, b):
    common = a.intersect(b)
    return common.val().Volume() if common.solids().size() else 0.0


def verify(name, device, device_mass, **settings):
    """Builds the stand and runs one check for each item in the prompt."""
    width, height, thickness = device
    stand, d = make_stand(width, height, thickness, **settings)
    body = stand.val()

    # 1. A single, valid solid?
    assert len(stand.solids().vals()) == 1, "Stand is not a single solid."
    assert body.isValid(), "Stand geometry is not valid."

    # 2. Are the outer dimensions as expected?
    box = body.BoundingBox()
    assert abs(box.ylen - d["width"]) < 0.01, "Width does not match."
    assert abs(box.xlen - d["base_depth"]) < 0.01, "Depth does not match."

    # 3. Does the device sit in the slot without overlap?
    device_block = device_model(d, width, height, thickness)
    overlap = common_volume(stand, device_block)
    assert overlap < 0.01, f"Device overlaps the stand: {overlap:.1f} mm3"

    # 4. Is the lip in front of the device?
    device_box = device_block.val().BoundingBox()
    assert d["lip_x"] + d["wall"] <= device_box.xmin + 0.01, \
        "The lip ends up inside the device."

    # 5. Tipping: is the combined centre of mass above the base?
    stand_mass = body.Volume() / 1000 * PLA_DENSITY
    c_stand = cq.Shape.centerOfMass(body)
    c_device = cq.Shape.centerOfMass(device_block.val())
    total = stand_mass + device_mass
    centre_x = (stand_mass * c_stand.x + device_mass * c_device.x) / total
    rear_margin = d["base_depth"] - centre_x
    nearest = min(centre_x, rear_margin)
    assert nearest >= 10, \
        f"Tipping risk: centre of mass {nearest:.1f} mm from the edge"

    print(f"{name}: 5 checks passed | stand {stand_mass:.0f} g | "
          f"rear margin {rear_margin:.1f} mm")
    return stand, device_block, d


if __name__ == "__main__":
    phone = verify("phone", (75, 160, 9), device_mass=180)
    tablet = verify("tablet", (180, 250, 8), device_mass=480, angle=70)
    cq.exporters.export(phone[0], "stand_phone.step")
    cq.exporters.export(tablet[0], "stand_tablet.step")
