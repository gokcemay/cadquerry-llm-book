"""Bir braket için tek sayfalık ölçü föyü (PNG ve PDF)."""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

KOYU, KIRMIZI = "#1f3a5f", "#b3261e"


def olcu(ax, p1, p2, yazi, kaydir=(0, 0), **kw):
    """İki nokta arasına ölçü oku ve yazısı."""
    ax.annotate("", xy=p1, xytext=p2,
                arrowprops=dict(arrowstyle="<->", color=KOYU, lw=0.8))
    ax.text((p1[0] + p2[0]) / 2 + kaydir[0], (p1[1] + p2[1]) / 2 + kaydir[1],
            yazi, fontsize=7.5, color=KOYU, ha="center", va="center", **kw)


def foy_ciz(p, ad, a, kutle, kural, dosya_govdesi):
    A, B, G = p["kol_a"], p["kol_b"], p["genislik"]
    t, r, d = p["kalinlik"], p["ic_yaricap"], p["delik_cap"]
    fig, (sol, sag) = plt.subplots(
        1, 2, figsize=(11.2, 5.4), dpi=150,
        gridspec_kw=dict(width_ratios=[3, 2]))

    # --- Sol: açınım ---
    sol.set_aspect("equal"); sol.axis("off")
    sol.set_title("Açınım (kesim çizimi)", fontsize=10, weight="bold")
    sol.add_patch(
        Rectangle((0, -G / 2), a["boy"], G, fc="#f3f4f6", ec="k", lw=1.2))
    for u in a["delikler"]:
        sol.add_patch(Circle((u, 0), d / 2, fc="white", ec="k", lw=1.0))
    ub = a["bukum_cizgisi"]
    sol.plot([ub, ub], [-G / 2, G / 2], color=KIRMIZI, lw=1.0, ls=(0, (6, 3)))
    sol.text(ub, G / 2 + 2, "büküm çizgisi, 90° yukarı", fontsize=7,
             color=KIRMIZI, ha="center", va="bottom")
    y = -G / 2 - 6
    olculer = sorted([(u, "") for u in a["delikler"]] + [(ub, " (büküm)")])
    for u, ek in olculer + [(a["boy"], " (boy)")]:
        olcu(sol, (0, y), (u, y), f"{u:.2f}{ek}", kaydir=(0, 2.2))
        y -= 6.5
    olcu(sol, (a["boy"] + 6, -G / 2), (a["boy"] + 6, G / 2), f"{G:g}",
         kaydir=(3.5, 0), rotation=90)
    sol.text(a["boy"] / 2, G / 2 + 8, f"{len(a['delikler'])} delik Ø{d:g}",
             fontsize=8, ha="center")
    sol.set_xlim(-8, a["boy"] + 16); sol.set_ylim(y - 4, G / 2 + 14)

    # --- Sağ: bükülmüş profil ---
    sag.set_aspect("equal"); sag.axis("off")
    sag.set_title("Yandan görünüş (bükülmüş)", fontsize=10, weight="bold")
    rd = r + t
    yay = [math.radians(v) for v in range(180, 271, 5)]
    dis = [(rd + rd * math.cos(v), rd + rd * math.sin(v)) for v in yay]
    ic = [(rd + r * math.cos(v), rd + r * math.sin(v)) for v in reversed(yay)]
    nokta = [(0, B)] + dis + [(A, 0), (A, t)] + ic + [(t, B)]
    sag.fill([q[0] for q in nokta], [q[1] for q in nokta],
             fc="#f3f4f6", ec="k", lw=1.2)
    olcu(sag, (0, -7), (A, -7), f"A = {A:g}", kaydir=(0, -3.5))
    olcu(sag, (-7, 0), (-7, B), f"B = {B:g}", kaydir=(-4, 0), rotation=90)
    sag.text(rd + 4, rd + 4, f"iç R{r:g}\nkalınlık {t:g}",
             fontsize=8, color=KOYU)
    sag.set_xlim(-16, A + 6); sag.set_ylim(-16, B + 6)

    fig.text(0.5, 0.035,
             f"{ad}   |   malzeme: çelik sac {t:g} mm   |   açınım boyu "
             f"{a['boy']:.1f} mm   |   bükme payı {a['bukme_payi']:.2f} mm "
             f"(k = {kural['k_faktoru']:g})   |   kütle {kutle:.0f} g",
             ha="center", fontsize=8.5,
             bbox=dict(boxstyle="square,pad=0.5", fc="white", ec="k", lw=0.8))
    fig.text(0.5, 0.955, "Ölçüler mm. Ölçü föyü; teknik resmin yerini tutmaz.",
             ha="center", fontsize=7.5, color="#555")
    fig.subplots_adjust(left=0.03, right=0.97, top=0.9, bottom=0.12,
                        wspace=0.05)
    fig.savefig(dosya_govdesi + ".png")
    fig.savefig(dosya_govdesi + ".pdf")
    plt.close(fig)
