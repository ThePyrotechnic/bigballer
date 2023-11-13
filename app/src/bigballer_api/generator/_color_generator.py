"""
bigballer web - collect items
    Copyright (C) 2023  Michael Manis - michaelmanis@tutanota.com
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

Thanks to https://paletton.com
Paletton's website helped immensely with testing these functions
and cross-checking results
"""
import colorsys
import random

from bigballer_api.generator import _color_tables


def _float_triplet_to_byte(a, b, c):
    return round(a * 255), round(b * 255), round(c * 255)


def hsv_to_hex(hue, sat, val):
    r, g, b = _float_triplet_to_byte(*colorsys.hsv_to_rgb(hue, sat, val))
    return f"0x{r:02x}{g:02x}{b:02x}"


def ryb_shift(hue, sat, val, degrees):
    """
    This will shift the color hue by degrees on a custom RYB color wheel
    NOT the RGB color wheel
    """
    ryb_hue = _color_tables.rgb_hue_lut[round(hue * 360 % 360)]
    shifted_hue = (ryb_hue + degrees / 360) % 1
    ryb_shifted = (_color_tables.ryb_hue_lut[round(shifted_hue * 360)], sat, val)
    return ryb_shifted


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


def generate_adjacent(hue, sat, val, degrees=30):
    return ryb_shift(hue, sat, val, 360 - degrees), ryb_shift(hue, sat, val, degrees)


def generate_triad(hue, sat, val, degrees=30):
    return (
        ryb_shift(hue, sat, val, degrees=180 - degrees),
        ryb_shift(hue, sat, val, degrees=180 + degrees),
    )


def generate_tetrad(hue, sat, val, degrees=30):
    opposite_color = ryb_shift(hue, sat, val, degrees=180)
    adjacent_color = ryb_shift(hue, sat, val, degrees=degrees)
    adjacent_to_opposite = ryb_shift(hue, sat, val, degrees=180 + degrees)
    return adjacent_color, opposite_color, adjacent_to_opposite
