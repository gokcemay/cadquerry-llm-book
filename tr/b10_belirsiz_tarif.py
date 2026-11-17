import cadquery as cq

# Aynı belirsiz tarifin üç makul yorumu:
# "Köşebent şeklinde bir bağlantı parçası yap, iki deliği olsun."


def kosebent(yatay, dikey, genislik, et):
    """L biçiminde köşebent: yatay kol X boyunca, dikey kol Z boyunca."""
    taban = cq.Workplane("XY").box(yatay, genislik, et, centered=(False, True, False))
    duvar = cq.Workplane("XY").box(et, genislik, dikey, centered=(False, True, False))
    return taban.union(duvar)


# Yorum A: eşit kollar, her kolda birer delik
a = kosebent(40, 40, 20, 3)
a = a.faces("<Z").workplane().pushPoints([(23, 0)]).hole(4.5, depth=3)
a = a.faces("<X").workplane().pushPoints([(0, 23)]).hole(4.5, depth=3)

# Yorum B: eşit kollar, iki delik de dikey kolda
b = kosebent(40, 40, 20, 3)
b = b.faces("<X").workplane().pushPoints([(0, 15), (0, 30)]).hole(4.5, depth=3)

# Yorum C: daha iri ve kalın, iç köşesi kavisli, iki delik de yatay kolda
c = kosebent(60, 30, 25, 5)
c = c.edges(cq.selectors.BoxSelector((4, -20, 4), (6, 20, 6))).fillet(6)
c = c.faces("<Z").workplane().pushPoints([(25, 0), (48, 0)]).hole(5.5, depth=5)

for ad, p in (("A", a), ("B", b), ("C", c)):
    k = p.val().BoundingBox()
    print(ad, k.xlen, k.ylen, k.zlen, round(p.val().Volume()),
          len(p.solids().vals()), p.val().isValid())
