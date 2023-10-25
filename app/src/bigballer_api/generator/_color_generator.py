"""
Thanks to https://paletton.com
Paletton's website helped immensely with testing these functions
This implementation ultimately does not line up with theirs, but
it is close
"""
import colorsys
import random


def _cubic_interp(t, a, b):
    weight = t * t * (3 - 2 * t)
    return a + weight * (b - a)


_RybWheel = (
    0,
    26,
    52,
    83,
    120,
    130,
    141,
    151,
    162,
    177,
    190,
    204,
    218,
    232,
    246,
    261,
    275,
    288,
    303,
    317,
    330,
    338,
    345,
    352,
    360,
)

_RgbWheel = (
    0,
    8,
    17,
    26,
    34,
    41,
    48,
    54,
    60,
    81,
    103,
    123,
    138,
    155,
    171,
    187,
    204,
    219,
    234,
    251,
    267,
    282,
    298,
    329,
    360,
)


def rgb_to_ryb(hue):
    d = hue % 15
    i = int(hue / 15)
    x0 = _RybWheel[i]
    x1 = _RybWheel[i + 1]
    return x0 + (x1 - x0) * d / 15


def ryb_to_rgb(r, y, b):
    # red
    x0, x1 = _cubic_interp(b, 1.0, 0.163), _cubic_interp(b, 1.0, 0.0)
    x2, x3 = _cubic_interp(b, 1.0, 0.5), _cubic_interp(b, 1.0, 0.2)
    y0, y1 = _cubic_interp(y, x0, x1), _cubic_interp(y, x2, x3)
    red = _cubic_interp(r, y0, y1)

    # green
    x0, x1 = _cubic_interp(b, 1.0, 0.373), _cubic_interp(b, 1.0, 0.66)
    x2, x3 = _cubic_interp(b, 0.0, 0.0), _cubic_interp(b, 0.5, 0.094)
    y0, y1 = _cubic_interp(y, x0, x1), _cubic_interp(y, x2, x3)
    green = _cubic_interp(r, y0, y1)

    # blue
    x0, x1 = _cubic_interp(b, 1.0, 0.6), _cubic_interp(b, 0.0, 0.2)
    x2, x3 = _cubic_interp(b, 0.0, 0.5), _cubic_interp(b, 0.0, 0.0)
    y0, y1 = _cubic_interp(y, x0, x1), _cubic_interp(y, x2, x3)
    blue = _cubic_interp(r, y0, y1)

    return red, green, blue


def _float_triplet_to_byte(a, b, c):
    return round(a * 255), round(b * 255), round(c * 255)


def hsv_to_hex(hue, sat, val):
    r, g, b = _float_triplet_to_byte(*colorsys.hsv_to_rgb(hue, sat, val))
    return f"0x{r:02x}{g:02x}{b:02x}"


def ryb_shift(hue, sat, val, degrees):
    """
    This will shift the color hue by degrees on the RYB color wheel
    NOT the RGB color wheel
    Thanks to https://stackoverflow.com/a/14116553
      which points to the conversion defined in the following paper:
    Nathan Gossett and Baoquan Chen. 2004.
      Paint Inspired Color Mixing and Compositing for Visualization.
      In Proceedings of the IEEE Symposium on Information Visualization (INFOVIS '04).
      IEEE Computer Society, USA, 113–118.
    """
    # This goes from:
    #   HSV -> RGB (intepreted as RYB) -> RGB -> HSV
    return colorsys.rgb_to_hsv(
        *ryb_to_rgb(*colorsys.hsv_to_rgb(degrees % 360 / 360 + hue % 1, sat, val))
    )


def random_color():
    # Hue, Sat, Val
    return random.random(), random.random(), random.random()


def generate_shades(hue, sat, val, max_distance=0.15, shade_pairs=2):
    def get_offsets(num):
        offsets = []
        total_desired_distance = max_distance * shade_pairs

        range_inc = range(1, shade_pairs + 1)
        range_dec = range(shade_pairs, 0, -1)
        if total_desired_distance > num:
            # Impossible to satisfy max distance
            # Instead, evenly separate values inside the available distance
            offsets.extend([num / (shade_pairs + 1) * a for a in range_inc])
        else:
            offsets.extend([num - max_distance * a for a in range_dec])
        offsets.append(num)

        if total_desired_distance + num > 1:
            offsets.extend([num + (1 - num) / (shade_pairs + 1) * a for a in range_inc])
        else:
            offsets.extend([num + max_distance * a for a in range_inc])

        return offsets

    sat_offsets = get_offsets(sat)
    val_offsets = get_offsets(val)

    # val should decrease as sat increases
    last_val_index = len(val_offsets) - 1
    return [
        (hue, sat_offsets[a], val_offsets[last_val_index - a])
        for a in range(shade_pairs * 2 + 1)
    ]


def generate_adjacent(hue, sat, val, degrees=60):
    return ryb_shift(hue, sat, val, 360 - degrees), ryb_shift(hue, sat, val, degrees)


def generate_triad(hue, sat, val, degrees=60):
    return (
        ryb_shift(hue, sat, val, degrees=180 - degrees),
        ryb_shift(hue, sat, val, degrees=180 + degrees),
    )


def generate_tetrad(hue, sat, val, degrees=60):
    opposite_color = ryb_shift(hue, sat, val, degrees=180)
    adjacent_color = ryb_shift(hue, sat, val, degrees=degrees)
    adjacent_to_opposite = ryb_shift(hue, sat, val, degrees=180 + degrees)
    return adjacent_color, opposite_color, adjacent_to_opposite
