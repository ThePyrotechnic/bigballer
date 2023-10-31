import colorsys


_colors = {
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

_interp_colors = [(1, 0, 0)]
_cur_step = _colors["0"]
_next_step = _colors["20"]
for a in range(1, 360):
    delta = a % 20
    if delta == 0:
        _interp_colors.append(_next_step)
        _cur_step = _next_step
        _next_step = _colors[str(a + 20)]
    else:
        c = (
            _cur_step[0] + (_next_step[0] - _cur_step[0]) * (delta / 20),
            _cur_step[1] + (_next_step[1] - _cur_step[1]) * (delta / 20),
            _cur_step[2] + (_next_step[2] - _cur_step[2]) * (delta / 20),
        )
        _interp_colors.append(c)

ryb_hue_lut = [colorsys.rgb_to_hsv(*c)[0] for c in _interp_colors]

rgb_hue_lut = [0]
_prev_value = 0
for key, value in enumerate(ryb_hue_lut[1:], 1):
    value_degrees = round(value * 360)
    if value_degrees == _prev_value:
        pass
    elif value_degrees == _prev_value + 1:
        rgb_hue_lut.append(key / 360)
    else:
        delta = value_degrees - _prev_value
        for a in range(1, delta):
            rgb_hue_lut.append((key - 1 + 1 / delta * a) / 360)
        rgb_hue_lut.append(key / 360)
    _prev_value = value_degrees
