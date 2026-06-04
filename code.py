import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Wedge
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe


outer_exc_col = "Exceedance_AESA"
inner_exc_col = "Exceedance_ASSA"


def add_fade_effect(ax, r1, r2, theta1, theta2, base_color, steps=100):
    rgba = mcolors.to_rgba(base_color)
    radii = np.linspace(r1, r2, steps + 1)

    for i in range(steps):
        rr1 = radii[i]
        rr2 = radii[i + 1]

        # strongest near the start, fades toward the outer end
        alpha = 1.0 - (i / (steps - 1))
        color = (rgba[0], rgba[1], rgba[2], alpha)

        ax.add_patch(
            Wedge(
                (0, 0),
                rr2,
                theta1,
                theta2,
                width=rr2 - rr1,
                facecolor=color,
                edgecolor='none',
                linewidth=0,
                zorder=6
            )
        )
        
plt.rcParams['font.family'] = 'Helvetica'

# --- Load and clean Sheet1 (outer ring) ---
raw1 = pd.read_excel("data_empty.xlsx", sheet_name="AESA", header=None)
raw1.columns = [
    "Code", "Category", "Impact",
    "Threshold_AESA", 
    "Exceedance_AESA", 
]
df_outer = raw1.iloc[2:].reset_index(drop=True)
for col in ["Impact", outer_exc_col]:
    df_outer[col] = pd.to_numeric(df_outer[col], errors="coerce").fillna(0)

# --- Load and clean Sheet2 (inner ring) ---
raw2 = pd.read_excel("data_empty.xlsx", sheet_name="ASSA", header=None)
raw2.columns = [
    "SocialFoundation", "Code", "Indicator", "Impact",
    "Threshold_ASSA", "Exceedance_ASSA",
]
# Skip metadata (row 1) and header (row 2), start from row 3
df_inner = raw2.iloc[2:].reset_index(drop=True)
for col in ["Impact", inner_exc_col]:
    df_inner[col] = pd.to_numeric(df_inner[col], errors="coerce").fillna(0)

n_outer = len(df_outer)
n_inner = len(df_inner)

# --- Geometry ---
r_label_gap = 0.01         # radial gap separating the label ring from data rings
gap_mid_to_sf = 0.0  # gap between mid ring and Social Foundation ring (to prevent overlap)

r_mid_center = 0.65        # center radius of the "Ecological Impact Base" ring
r_mid_width = 0.08         # thickness of the "Ecological Impact Base" ring

r_mid_inner = r_mid_center - r_mid_width / 2
r_mid_outer = r_mid_center + r_mid_width / 2

r_sf_width = 0.08          # thickness of the Social Foundation category ring (inside Ecological ring)
r_sf_outer = r_mid_inner - gap_mid_to_sf
r_sf_inner = r_sf_outer - r_sf_width

r_outer_base = r_mid_outer + r_label_gap  # outer ring starts here (outer margin for label ring)
r_inner_base = r_sf_inner - r_label_gap   # inner ring ends here (leave margin under Social Foundation ring)

r_range_outer = 0.60       # outer ring extends outward
r_range_inner = 0.36       # inner ring extends inward (keeps radii > 0)

r_outer_max = r_outer_base + r_range_outer
r_inner_min = r_inner_base - r_range_inner
GAP = 0.1  # degrees gap between slices

# Update the color palette for the graph
GREEN = "#a0d2a5ff"
ORANGE = "#f5be78ff"
RED = "#d76455ff"
GREY = "#BDBDBD"
GREY2 = "#f2f2f2ff"

# --- Shared log axis: exceedance [0, 100] ---
EXC_MAX = 1000.0
LOG_MAX = np.log10(1 + EXC_MAX)


def exc_to_r_outer(exc_val):
    """Exceedance -> radius growing outward from boundary."""
    clamped = np.clip(exc_val, 0, EXC_MAX)
    return r_outer_base + (np.log10(1 + clamped) / LOG_MAX) * r_range_outer


def exc_to_r_inner(exc_val):
    """Exceedance -> radius growing inward from boundary."""
    clamped = np.clip(exc_val, 0, EXC_MAX)
    r = r_inner_base - (np.log10(1 + clamped) / LOG_MAX) * r_range_inner
    return max(0.01, r)


# Fixed boundary radii (outer ring)
R_OUT_1 = exc_to_r_outer(1.0)
R_OUT_10 = exc_to_r_outer(10.0)
# Fixed boundary radii (inner ring — note: these go inward, so R_IN_1 > R_IN_10)
R_IN_1 = exc_to_r_inner(1.0)
R_IN_10 = exc_to_r_inner(10.0)

# --- Draw ---
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_aspect("equal")
ax.set_xlim(-1.75, 1.75)
ax.set_ylim(-1.75, 1.75)
ax.axis("off")



def add_wedge(r1, r2, theta1, theta2, color):
    """Draw a wedge from r1 (inner) to r2 (outer)."""
    if r2 <= r1 + 1e-6:
        return
    ax.add_patch(
        Wedge(
            (0, 0), r2, theta1, theta2,
            width=r2 - r1,
            facecolor=color, edgecolor="white", linewidth=0.8,
        )
    )

# Helper function to add a fade effect wedge
def add_fade_wedge(r1, r2, theta1, theta2, base_color, steps=100):
    """Add a fade effect by splitting the wedge into thin radial wedges with decreasing alpha."""
    for i in range(steps):
        alpha = 1.0 - (i / steps) * 0.7  # Gradual fade from 1.0 to 0.1
        inner_r = r1 + (i / steps) * (r2 - r1)
        outer_r = r1 + ((i + 1) / steps) * (r2 - r1)
        ax.add_patch(
            Wedge(
                (0, 0), outer_r, theta1, theta2,
                width=outer_r - inner_r,
                facecolor=base_color,
                edgecolor="none",
                alpha=alpha, zorder=1000,  # Increased zorder for visibility
            )
        )

def text_on_arc(text, radius, theta_center_deg=90.0, arc_span_deg=220.0, **kwargs):
    """
    Draw text following a circular arc (character by character).

    theta_center_deg: where the text is centered (degrees).
    arc_span_deg: total angular span used by the string (degrees).
    """
    if not text:
        return


    n = len(text)
    theta_start = theta_center_deg + arc_span_deg / 2
    theta_end = theta_center_deg - arc_span_deg / 2
    thetas = np.linspace(theta_start, theta_end, n)

    for ch, th in zip(text, thetas):
        ang = np.deg2rad(th)
        x, y = radius * np.cos(ang), radius * np.sin(ang)


        rot = th - 90
        if rot < -90:
            rot += 180
        elif rot > 90:
            rot -= 180

        ax.text(
            x, y, ch,
            rotation=th - 90,
            rotation_mode="anchor",
            ha="center", va="center",
            **kwargs,
        )


# ===================== ECOLOGICAL IMPACT BASE RING =====================
ax.add_patch(
    Wedge(
        (0, 0), r_mid_outer, 0, 360,
        width=r_mid_outer - r_mid_inner,
        facecolor="#f2f2f2ff",  # Background color remains f2f2f2ff
        edgecolor="#999999ff",  # Updated outline color to 999999ff
        linewidth=0.8, zorder=3,
    )
)
# Update the font size and style for the "Ecological Impact Base" label
text_on_arc(
    "Ecological Impact Base",
    radius=(r_mid_inner + r_mid_outer) / 2,  # Adjusted radius for the label
    theta_center_deg=90.0,
    arc_span_deg=70.0,  # Reduced arc span to bring letters closer
    fontsize=7,  # Smaller font size
    fontweight="normal",  # Non-bold font
    color="black", zorder=4,
)


# Precompute angular width (used by Social Foundation + inner ring)
slice_deg_inner = 360.0 / n_inner

# ===================== SOCIAL FOUNDATION RING (Sheet2 categories) =====================
# One wedge per SocialFoundation, spanning from the first code in that category
# to the last code in that category (based on the inner-ring ordering).
sf_series = df_inner["SocialFoundation"].fillna("Unknown").astype(str)
unique_foundations = sf_series.drop_duplicates().tolist()
sf_cmap = plt.get_cmap("tab20")
sf_color_map = {k: sf_cmap(i % sf_cmap.N) for i, k in enumerate(unique_foundations)}

sf_spans = []
for foundation in unique_foundations:
    idxs = np.where(sf_series.values == foundation)[0]
    if len(idxs) == 0:
        continue
    sf_spans.append((foundation, int(idxs.min()), int(idxs.max())))

# draw in angular order
sf_spans.sort(key=lambda t: t[1])

line_r = r_sf_inner + 0.70 * (r_sf_outer - r_sf_inner)  # radius at which to draw the boundary lines
boundary_angles =[]



for foundation, idx_start, idx_end in sf_spans:
    th_start = 90.0 - idx_start * slice_deg_inner - GAP / 2
    th_end = 90.0 - (idx_end + 1) * slice_deg_inner + GAP / 2
    boundary_angles.extend([th_start, th_end])

boundary_angles = sorted(set(round(th, 6) for th in boundary_angles))

for th in boundary_angles:
    ang = np.deg2rad(th)
    ax.plot(
        [0, line_r * np.cos(ang)],
        [0, line_r * np.sin(ang)],
        color="#c8c8c8", 
        linewidth=0.25, 
        zorder=5,
    )




for foundation, idx_start, idx_end in sf_spans:
    # span from the start of idx_start slice to the end of idx_end slice
    th2 = 90.0 - idx_start * slice_deg_inner - GAP / 2
    th1 = 90.0 - (idx_end + 1) * slice_deg_inner + GAP / 2

  

    mid_deg_sf = (th1 + th2) / 2
    label_r_sf = (r_sf_inner + r_sf_outer) / 2
    span_deg = abs(th2 - th1)
    arc_span_sf = max(10.0, min(span_deg * 0.85, max(18.0, len(foundation) * 2.2)))
    if foundation.strip().lower() == "political voice":
        dr = (r_sf_outer - r_sf_inner) * 0.18
        text_on_arc(
            "Political",
            radius=label_r_sf + dr,
            theta_center_deg=mid_deg_sf,
            arc_span_deg=min(arc_span_sf, 550.0),
            fontsize=6,
            fontweight="normal",
            color="black",
            zorder=6,
        )
        text_on_arc(
            "Voice",
            radius=label_r_sf - dr,
            theta_center_deg=mid_deg_sf,
            arc_span_deg=min(arc_span_sf, 35.0),
            fontsize=6,
            fontweight="normal",
            color="black",
            zorder=6,
        )
    else:
        text_on_arc(
            foundation,
            radius=label_r_sf,
            theta_center_deg=mid_deg_sf,
            arc_span_deg=arc_span_sf,
            fontsize=6,
            fontweight="normal",
            color="black",
            zorder=6,
        )


# ===================== OUTER RING (Sheet1, Eq1) =====================
slice_deg_outer = 360.0 / n_outer

for i, row in df_outer.iterrows():
    exc = float(row[outer_exc_col])
    code = row["Code"]

    th2 = 90.0 - i * slice_deg_outer - GAP / 2
    th1 = th2 - slice_deg_outer + GAP

    outer_r = exc_to_r_outer(exc)

    if exc <= 0:
        add_wedge(r_outer_base, r_outer_base + 0.01, th1, th2, GREEN)
    elif exc < 1:
        add_wedge(r_outer_base, outer_r, th1, th2, GREEN)
    elif exc <= 10:
        add_wedge(r_outer_base, R_OUT_1, th1, th2, GREEN)
        add_wedge(R_OUT_1, outer_r, th1, th2, ORANGE)
    else:
        add_wedge(r_outer_base, R_OUT_1, th1, th2, GREEN)
        add_wedge(R_OUT_1, R_OUT_10, th1, th2, ORANGE)
        fade_side_gap = 0.1
        add_fade_wedge(R_OUT_10, outer_r, th1 + fade_side_gap, th2 - fade_side_gap, RED)

    # Outer label
    mid_rad = np.deg2rad((th1 + th2) / 2)
    lbl_r = r_outer_max + 0.1
    x, y = lbl_r * np.cos(mid_rad), lbl_r * np.sin(mid_rad)
    ax.text(x, y, code,
            ha="left" if x >= 0 else "right",
            va="center", fontsize=7, fontweight="bold")


# ===================== INNER RING (Sheet2, SSB) =====================
for i, row in df_inner.iterrows():
    exc = float(row[inner_exc_col])
    code = row["Code"]

    th2 = 90.0 - i * slice_deg_inner - GAP / 2
    th1 = th2 - slice_deg_inner + GAP

    inner_r = exc_to_r_inner(exc)  # this is smaller than r_inner_base

    if exc <= 0:
        add_wedge(r_inner_base - 0.01, r_inner_base, th1, th2, GREEN)
    elif exc < 1:
        # Green from boundary inward to inner_r
        add_wedge(inner_r, r_inner_base, th1, th2, GREEN)
    elif exc <= 10:
        # Green from boundary to R_IN_1, orange from R_IN_1 to inner_r
        add_wedge(R_IN_1, r_inner_base, th1, th2, GREEN)
        add_wedge(inner_r, R_IN_1, th1, th2, ORANGE)
    else:
        # Green from boundary to R_IN_1, orange to R_IN_10, red to inner_r
        add_wedge(R_IN_1, r_inner_base, th1, th2, GREEN)
        add_wedge(R_IN_10, R_IN_1, th1, th2, ORANGE)
        fade_side_gap = 0.1
        add_fade_wedge(R_IN_10, inner_r, th1 + fade_side_gap, th2 - fade_side_gap, RED, steps=200)

    # Inner label moved to a fixed radius just below the Social Foundation name ring
    mid_deg = (th1 + th2) / 2
    mid_rad = np.deg2rad(mid_deg)
    code_label_offset = 0.01  # small offset to prevent overlap with Social Foundation labels
    label_r = r_sf_inner + code_label_offset # Fixed radius just inside r_sf_inner

    arc_span = max(1.0, min(6.0, len(str(code)) * 2.0))  # very low letter spacing
    text_on_arc(
        str(code),
        radius=label_r,
        theta_center_deg=mid_deg,
        arc_span_deg=arc_span,
        fontsize=5, 
        color="black",
        zorder=6,
    )


# --- Reference circles at exc=1 and exc=10 (both rings) ---
for r, lbl in [(R_OUT_1, "1"), (R_OUT_10, "10")]:
    ax.add_patch(plt.Circle((0, 0), r, fill=False,
                             linestyle="--", linewidth=0.5, color="grey", zorder=4, alpha=0.4))
for r, lbl in [(R_IN_1, "1"), (R_IN_10, "10")]:
    ax.add_patch(plt.Circle((0, 0), r, fill=False,
                             linestyle="--", linewidth=0.5, color="grey", zorder=4, alpha=0.4))






# Center white circle
center_circle = plt.Circle(
    (0, 0),
    0.00,
    facecolor="white",
    edgecolor="#c8c8c8",
    linewidth=0.25,
    zorder=2000
)

ax.add_patch(center_circle)








# -----------------
# LEGEND FOR COLOR CODING
# --------


# Add legend below the circle
legend_elements = [
    mpatches.Patch(color=GREEN, label="Within the absolute boundaries"),
    mpatches.Patch(color=ORANGE, label="Exceeding up to 10x"),
    mpatches.Patch(color=RED, label="Exceeding >10x")
]
ax.legend(
    handles=legend_elements,
    loc="lower center",
    bbox_to_anchor=(0.5, 0.05),  # Move closer to the circle
    ncol=3,
    frameon=False,
    fontsize=8
)




# Adjust layout to ensure the legend is visible
plt.subplots_adjust(bottom=0.80)

plt.tight_layout()
plt.savefig("graph_a_(Eq1+SSB).png", dpi=150, bbox_inches="tight")
plt.savefig("graph_a_(Eq1+SSB).pdf", bbox_inches="tight")
plt.savefig("graph_a_(Eq1+SSB).svg", bbox_inches="tight")
plt.show()


