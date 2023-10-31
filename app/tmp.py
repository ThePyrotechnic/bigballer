from bigballer_api.generator import _color_generator as gen
from bigballer_api.generator import _color_tables as tb

import colorsys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
import matplotlib as mpl


fig = plt.figure()

display_axes = fig.add_axes([0.1, 0.1, 0.8, 0.8], projection="polar")
display_axes._direction = 2 * np.pi

norm = mpl.colors.Normalize(0.0, 2 * np.pi)

# colors = [colorsys.hsv_to_rgb(h, 1, 1) for h in tb._rgb_hue_lut]
# colors = [colorsys.hsv_to_rgb(a / quant_steps, 1, 1) for a in range(2048)]
colors = {
    "0": (1, 0, 0),
    "20": (1, 89 / 255, 0),
    "40": (1, 137 / 255, 0),
    "60": (1, 170 / 255, 0),
    "80": (1, 198 / 255, 0),
    "100": (1, 225 / 255, 0),
    "120": (1, 1, 0),
    "140": (198 / 255, 1, 0),
    "160": (137 / 255, 1, 0),
    "180": (0, 1, 0),
    "200": (0, 1, 178 / 255),
    "220": (0, 172 / 255, 1),
    "240": (0, 77 / 255, 1),
    "260": (23 / 255, 0, 1),
    "280": (93 / 255, 0, 1),
    "300": (164 / 255, 0, 1),
    "320": (1, 0, 207 / 255),
    "340": (1, 0, 99 / 255),
    "360": (1, 0, 0),
}

interp_colors = [(1, 0, 0)]
cur_step = colors["0"]
next_step = colors["20"]
for a in range(1, 360):
    delta = a % 20
    if delta == 0:
        interp_colors.append(next_step)
        cur_step = next_step
        next_step = colors[str(a + 20)]
    else:
        c = (
            cur_step[0] + (next_step[0] - cur_step[0]) * (delta / 20),
            cur_step[1] + (next_step[1] - cur_step[1]) * (delta / 20),
            cur_step[2] + (next_step[2] - cur_step[2]) * (delta / 20),
        )
        interp_colors.append(c)

interp_hsv = [colorsys.rgb_to_hsv(*c) for c in interp_colors]
for a in range(360):
    print(a, round(interp_hsv[a][0] * 360))

map = ListedColormap(interp_colors)
cb = mpl.colorbar.ColorbarBase(
    display_axes, cmap=map, norm=norm, orientation="horizontal"
)

cb.outline.set_visible(False)
display_axes.set_axis_off()
plt.savefig("tmp.png")
