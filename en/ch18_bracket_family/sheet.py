"""One-page dimension sheet for a bracket (PNG and PDF)."""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

DARK, RED = "#1f3a5f", "#b3261e"


def dimension(ax, p1, p2, label, shift=(0, 0), **kw):
    """A dimension arrow between two points, with its label."""
    ax.annotate("", xy=p1, xytext=p2,
                arrowprops=dict(arrowstyle="<->", color=DARK, lw=0.8))
    ax.text((p1[0] + p2[0]) / 2 + shift[0], (p1[1] + p2[1]) / 2 + shift[1],
            label, fontsize=7.5, color=DARK, ha="center", va="center", **kw)


def draw_sheet(p, name, a, mass, rules, file_stem):
    A, B, W = p["arm_a"], p["arm_b"], p["width"]
    t, r, d = p["thickness"], p["inner_radius"], p["hole_dia"]
    fig, (left, right) = plt.subplots(
        1, 2, figsize=(11.2, 5.4), dpi=150,
        gridspec_kw=dict(width_ratios=[3, 2]))

    # --- Left: flat pattern ---
    left.set_aspect("equal"); left.axis("off")
    left.set_title("Flat pattern (cutting drawing)", fontsize=10, weight="bold")
    left.add_patch(
        Rectangle((0, -W / 2), a["length"], W, fc="#f3f4f6", ec="k", lw=1.2))
    for u in a["holes"]:
        left.add_patch(Circle((u, 0), d / 2, fc="white", ec="k", lw=1.0))
    ub = a["bend_line"]
    left.plot([ub, ub], [-W / 2, W / 2], color=RED, lw=1.0, ls=(0, (6, 3)))
    left.text(ub, W / 2 + 2, "bend line, 90° up", fontsize=7,
              color=RED, ha="center", va="bottom")
    y = -W / 2 - 6
    dims = sorted([(u, "") for u in a["holes"]] + [(ub, " (bend)")])
    for u, extra in dims + [(a["length"], " (length)")]:
        dimension(left, (0, y), (u, y), f"{u:.2f}{extra}", shift=(0, 2.2))
        y -= 6.5
    dimension(left, (a["length"] + 6, -W / 2), (a["length"] + 6, W / 2), f"{W:g}",
              shift=(3.5, 0), rotation=90)
    left.text(a["length"] / 2, W / 2 + 8, f"{len(a['holes'])} holes Ø{d:g}",
              fontsize=8, ha="center")
    left.set_xlim(-8, a["length"] + 16); left.set_ylim(y - 4, W / 2 + 14)

    # --- Right: bent profile ---
    right.set_aspect("equal"); right.axis("off")
    right.set_title("Side view (bent)", fontsize=10, weight="bold")
    ro = r + t
    arc = [math.radians(v) for v in range(180, 271, 5)]
    outer = [(ro + ro * math.cos(v), ro + ro * math.sin(v)) for v in arc]
    inner = [(ro + r * math.cos(v), ro + r * math.sin(v)) for v in reversed(arc)]
    pts = [(0, B)] + outer + [(A, 0), (A, t)] + inner + [(t, B)]
    right.fill([q[0] for q in pts], [q[1] for q in pts],
               fc="#f3f4f6", ec="k", lw=1.2)
    dimension(right, (0, -7), (A, -7), f"A = {A:g}", shift=(0, -3.5))
    dimension(right, (-7, 0), (-7, B), f"B = {B:g}", shift=(-4, 0), rotation=90)
    right.text(ro + 4, ro + 4, f"inner R{r:g}\nthickness {t:g}",
               fontsize=8, color=DARK)
    right.set_xlim(-16, A + 6); right.set_ylim(-16, B + 6)

    fig.text(0.5, 0.035,
             f"{name}   |   material: steel sheet {t:g} mm   |   flat length "
             f"{a['length']:.1f} mm   |   bend allowance {a['bend_allowance']:.2f} mm "
             f"(k = {rules['k_factor']:g})   |   mass {mass:.0f} g",
             ha="center", fontsize=8.5,
             bbox=dict(boxstyle="square,pad=0.5", fc="white", ec="k", lw=0.8))
    fig.text(0.5, 0.955, "Dimensions in mm. A dimension sheet; not a substitute for an engineering drawing.",
             ha="center", fontsize=7.5, color="#555")
    fig.subplots_adjust(left=0.03, right=0.97, top=0.9, bottom=0.12,
                        wspace=0.05)
    fig.savefig(file_stem + ".png")
    fig.savefig(file_stem + ".pdf")
    plt.close(fig)
