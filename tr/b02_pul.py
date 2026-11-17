import cadquery as cq

# 40 mm dış çaplı, 16 mm delikli, 6 mm kalınlığında bir pul
pul = cq.Workplane("XY").circle(20).circle(8).extrude(6)

# Aynı katı, iki farklı hassasiyetle üçgen ağa çevriliyor
cq.exporters.export(pul, "pul_kaba.stl",
                    tolerance=1.5, angularTolerance=0.6)
cq.exporters.export(pul, "pul_ince.stl",
                    tolerance=0.01, angularTolerance=0.1)
