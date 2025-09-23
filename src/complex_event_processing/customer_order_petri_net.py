# petri_order_process_matplotlib.py
# Draws a Petri net for the restaurant example using only matplotlib.

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch

# --- tiny drawing helpers -----------------------------------------------------
def place(ax, xy, r=0.25, label=None):
    c = Circle(xy, r, fill=False, linewidth=2, zorder=3)
    ax.add_patch(c)
    if label:
        ax.text(xy[0], xy[1]+0.55, label, ha='center', va='bottom', fontsize=10)
    return c

def transition(ax, xy, w=0.7, h=0.35, label=None):
    # xy is center
    rect = Rectangle((xy[0]-w/2, xy[1]-h/2), w, h, fill=False, linewidth=2, zorder=3)
    ax.add_patch(rect)
    if label:
        ax.text(xy[0], xy[1]+0.55, label, ha='center', va='bottom', fontsize=10)
    return rect

def arrow(ax, p_from, p_to, curve=0.0, color='tab:blue', style='simple', lw=2, dash=False):
    # p_from/p_to are (x, y) centers. We draw center-to-center with a little shrink.
    connstyle = f"arc3,rad={curve}" if curve != 0 else "arc3"
    a = FancyArrowPatch(p_from, p_to, arrowstyle='-|>', mutation_scale=12,
                        linewidth=lw, color=color, shrinkA=12, shrinkB=12,
                        connectionstyle=connstyle)
    if dash:
        a.set_linestyle('--')
    ax.add_patch(a)

def step_number(ax, xy, n):
    circ = Circle(xy, 0.22, facecolor='white', edgecolor='red', linewidth=2, zorder=4)
    ax.add_patch(circ)
    ax.text(xy[0], xy[1], str(n), ha='center', va='center', color='red', fontsize=10, zorder=5)

# --- layout (x,y) coordinates -------------------------------------------------
# Top lane (customer-facing)
y_top = 1.5
x = {
    "p_arrive": 0.5,
    "t_arrive": 1.6,
    "p_seated": 2.6,
    "t_order": 3.7,
    "p_order_placed": 4.7,
    "p_order_ready_sync": 6.3,
    "t_served": 7.4,
    "p_end": 8.4
}

# Bottom lane (kitchen)
y_bot = 0.0
xb = {
    "p_order_trigger": 4.7,      # same x as p_order_placed to show the split
    "t_begin": 5.6,
    "p_mid1": 6.6,
    "t_cook": 7.6,
    "p_mid2": 8.6,
    "t_ready": 9.6
}

fig, ax = plt.subplots(figsize=(11, 3.8))

# --- draw top lane places/transitions -----------------------------------------
p1 = place(ax, (x["p_arrive"], y_top), label="Arrive")
t1 = transition(ax, (x["t_arrive"], y_top), label="")  # Arrive transition box (label above 'Arrive')
ax.text(x["t_arrive"], y_top+0.55, "Arrive", ha='center', va='bottom', fontsize=10)

p2 = place(ax, (x["p_seated"], y_top), label="Seated")
t2 = transition(ax, (x["t_order"], y_top), label="Order")
p3 = place(ax, (x["p_order_placed"], y_top))  # unlabeled place; see step numbers
p_sync = place(ax, (x["p_order_ready_sync"], y_top), label="Order Ready")
t3 = transition(ax, (x["t_served"], y_top), label="Served")
p_end = place(ax, (x["p_end"], y_top))

# Arrows (top lane)
arrow(ax, (x["p_arrive"], y_top), (x["t_arrive"], y_top))
arrow(ax, (x["t_arrive"], y_top), (x["p_seated"], y_top))
arrow(ax, (x["p_seated"], y_top), (x["t_order"], y_top))
arrow(ax, (x["t_order"], y_top), (x["p_order_placed"], y_top))
arrow(ax, (x["p_order_ready_sync"], y_top), (x["t_served"], y_top))
arrow(ax, (x["t_served"], y_top), (x["p_end"], y_top))

# --- draw bottom lane places/transitions --------------------------------------
p_trig = place(ax, (xb["p_order_trigger"], y_bot), label="Order")
t_begin = transition(ax, (xb["t_begin"], y_bot), label="Order Begin")
p_mid1 = place(ax, (xb["p_mid1"], y_bot))
t_cook = transition(ax, (xb["t_cook"], y_bot), label="Order Cooking")
p_mid2 = place(ax, (xb["p_mid2"], y_bot))
t_ready = transition(ax, (xb["t_ready"], y_bot), label="Order Ready")

# Arrows (bottom lane)
arrow(ax, (xb["p_order_trigger"], y_bot), (xb["t_begin"], y_bot))
arrow(ax, (xb["t_begin"], y_bot), (xb["p_mid1"], y_bot))
arrow(ax, (xb["p_mid1"], y_bot), (xb["t_cook"], y_bot))
arrow(ax, (xb["t_cook"], y_bot), (xb["p_mid2"], y_bot))
arrow(ax, (xb["p_mid2"], y_bot), (xb["t_ready"], y_bot))

# --- split & rejoin -----------------------------------------------------------
# Split: top p_order_placed -> bottom p_order_trigger
arrow(ax, (x["p_order_placed"], y_top), (xb["p_order_trigger"], y_bot), curve=-0.35)

# Rejoin: bottom t_ready -> top p_order_ready_sync
arrow(ax, (xb["t_ready"], y_bot), (x["p_order_ready_sync"], y_top), curve=0.35, dash=True)

""" --- step numbers -------------------------------------------------------------
step_number(ax, (x["p_arrive"]-0.35, y_top), 1)         # 1. Customer walks in
step_number(ax, (x["t_order"], y_top+0.85), 2)          # 2. Customer orders
step_number(ax, (x["p_order_placed"], y_top+0.85), 3)   # 3. Order event fired (caseId)
step_number(ax, (xb["p_order_trigger"], y_bot-0.8), 4)  # 4. Order triggers prep
step_number(ax, (xb["t_ready"], y_bot-0.8), 5)          # 5. Order is ready
step_number(ax, (x["p_order_ready_sync"]+0.35, y_top+0.85), 6)  # 6. Order Ready fired (same caseId)
"""
# --- cosmetics ----------------------------------------------------------------
ax.set_xlim(0, 10.3)
ax.set_ylim(-1.4, 2.3)
ax.axis('off')
ax.set_title("Restaurant Process as a Petri Net (Parallel lanes rejoin on Order Ready)", fontsize=12)

plt.tight_layout()
plt.savefig("c:\\temp\\petri_order_process_matplotlib.png", dpi=200)
plt.show()
