import cadquery as cq

# Kulaklık askısının (Bölüm 12) yalnızca sınanacak kısımlarını ayırır.
# Bütün parçayı basmadan önce bu küçük parçalar basılır ve denenir.

aski = cq.importers.importStep("kulaklik_askisi.step")


def kesit(parca, x, y, z):
    """Parçanın verilen aralıklarda kalan kısmı. Her aralık: (alt, üst)."""
    kutu = (
        cq.Workplane("XY")
        .box(x[1] - x[0], y[1] - y[0], z[1] - z[0], centered=False)
        .translate((x[0], y[0], z[0]))
    )
    return parca.intersect(kutu)


# Vida kesiti: plakanın iki deliği taşıyan ucu. Vida ve havşa uyumu için.
vida_kesiti = kesit(aski, (-12.5, 12.5), (44, 80), (-5, 0))

# Profil dilimi: kenardan 3 mm'lik dilim. Bant açıklığı ve tırnak için.
profil_dilimi = kesit(aski, (9.5, 12.5), (0, 80), (-55, 0))

# --- Ölç ---
tam = aski.val().Volume()
for ad, p in [("vida kesiti", vida_kesiti), ("profil dilimi", profil_dilimi)]:
    k = p.val().BoundingBox()
    v = p.val().Volume()
    print(f"{ad}: {k.xlen:.1f} x {k.ylen:.1f} x {k.zlen:.1f} mm |",
          f"kati: {p.solids().size()} |",
          f"hacim: {v:.0f} mm3 (%{100 * v / tam:.0f})")

cq.exporters.export(vida_kesiti, "aski_vida_kesiti.stl",
                    tolerance=0.05, angularTolerance=0.2)
cq.exporters.export(profil_dilimi, "aski_profil_dilimi.stl",
                    tolerance=0.05, angularTolerance=0.2)
