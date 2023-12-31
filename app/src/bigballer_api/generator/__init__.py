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
"""
import math
from pathlib import Path
import random

import boto3

from bigballer_api.settings import settings
from bigballer_api.generator._words import modifiers, names, appraisals
from bigballer_api.generator import _blender_generator, _color_generator


rarity_names = ["common", "notable", "pristine", "sublime", "transcendant"]

rarity_table = {}
rarity_table[rarity_names[4]] = 1 / 391  # transcendant
rarity_table[rarity_names[3]] = 1 / 156  # sublime
rarity_table[rarity_names[2]] = 1 / 31.3  # pristine
rarity_table[rarity_names[1]] = 1 / 6.26  # notable
# rarity_table[rarity_names[0]] = 1 / 1.25  # common

material_rarity_table = {}
material_rarity_table[rarity_names[4]] = [
    {
        "name": "diamond",
        "metalness": 0,
        "transmission": 1,
        "thickness": 0.1,
        "roughness": 0,
        "ior": 2.4168,
        "colors": [{"hsv": (0, 0, 1), "hue_variance": 5}],
    },
    {
        "name": "gold",
        "metalness": 1,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {"hsv": (0.11762988908347931, 0.6048728813559322, 0.944), "hue_variance": 5}
        ],
    },
]
material_rarity_table[rarity_names[3]] = [
    {
        "name": "sapphire",
        "metalness": 0,
        "transmission": 1,
        "thickness": 0.1,
        "roughness": 0,
        "ior": 1.7682,
        "colors": [
            {"hsv": (0.5819819819819819, 0.21637426900584789, 0.855), "hue_variance": 5}
        ],
    },
    {
        "name": "silver",
        "metalness": 1,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {
                "hsv": (0.11249999999999986, 0.041580041580041506, 0.962),
                "hue_variance": 5,
            }
        ],
    },
    {
        "name": "platinum",
        "metalness": 1,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {"hsv": (0.0989010989010989, 0.13402061855670114, 0.679), "hue_variance": 5}
        ],
    },
]
material_rarity_table[rarity_names[2]] = [
    {
        "name": "chromium",
        "metalness": 1,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {"hsv": (0.5800000000000001, 0.03770739064856715, 0.663), "hue_variance": 5}
        ],
    },
    {
        "name": "blood",
        "metalness": 0,
        "transmission": 1,
        "thickness": 0.2,
        "roughness": 0.1,
        "ior": 1.301,
        "colors": [
            {"hsv": (0.999479979199168, 0.9953416149068323, 0.644), "hue_variance": 5}
        ],
    },
    {
        "name": "glass",
        "metalness": 0,
        "transmission": 1,
        "thickness": 0,
        "ior": 1.52,
        "colors": [{"hsv": (0, 0, 1), "hue_variance": 5}],
    },
    {
        "name": "honey",
        "metalness": 0,
        "transmission": 1,
        "thickness": 0.3,
        "roughness": 0.1,
        "ior": 1.504,
        "colors": [
            {"hsv": (0.07545187053383774, 0.9542719614921781, 0.831), "hue_variance": 5}
        ],
    },
]
material_rarity_table[rarity_names[1]] = [
    {
        "name": "brass",
        "metalness": 1,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {"hsv": (0.13061074319352464, 0.5107102593010147, 0.887), "hue_variance": 5}
        ],
    },
    {
        "name": "chocolate",
        "metalness": 0,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {"hsv": (0.05065359477124184, 0.6296296296296297, 0.162), "hue_variance": 5}
        ],
    },
    {
        "name": "aluminum",
        "metalness": 1,
        "transmission": 0,
        "ior": 1.5,
        "colors": [{"hsv": (0.625, 0.00869565217391305, 0.92), "hue_variance": 5}],
    },
    {
        "name": "copper",
        "metalness": 1,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {"hsv": (0.0857030015797788, 0.4557235421166307, 0.926), "hue_variance": 5}
        ],
    },
    {
        "name": "water",
        "metalness": 0,
        "transmission": 1,
        "thickness": 0.01,
        "roughness": 0,
        "ior": 1.3325,
        "colors": [{"hsv": (0.59444, 0.07843, 1), "hue_variance": 5}],
    },
    {
        "name": "ice",
        "metalness": 0,
        "transmission": 1,
        "thickness": 0.05,
        "roughness": 0.1,
        "ior": 1.3098,
        "colors": [{"hsv": (0, 0, 1), "hue_variance": 5}],
    },
    {
        "name": "iron",
        "metalness": 1,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {"hsv": (0.0761904761904762, 0.06591337099811681, 0.531), "hue_variance": 5}
        ],
    },
    {
        "name": "nickel",
        "metalness": 1,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {
                "hsv": (0.10648148148148141, 0.16640986132511554, 0.649),
                "hue_variance": 5,
            }
        ],
    },
]
material_rarity_table[rarity_names[0]] = [
    {
        "name": "bone",
        "metalness": 0,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {"hsv": (0.16666666666666666, 0.1626733921815889, 0.793), "hue_variance": 5}
        ],
    },
    {
        "name": "brick",
        "metalness": 0,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {"hsv": (0.028192371475953566, 0.767175572519084, 0.262), "hue_variance": 5}
        ],
    },
    {
        "name": "charcoal",
        "metalness": 0,
        "transmission": 0,
        "ior": 1.5,
        "colors": [{"hsv": (0, 0, 0.02), "hue_variance": 5}],
    },
    {
        "name": "concrete",
        "metalness": 0,
        "transmission": 0,
        "ior": 1.5,
        "colors": [{"hsv": (0, 0, 0.51), "hue_variance": 5}],
    },
    {
        "name": "egg shell",
        "metalness": 0,
        "transmission": 0,
        "ior": 1.5,
        "colors": [
            {
                "hsv": (0.5555555555555555, 0.033280507131537275, 0.631),
                "hue_variance": 5,
            }
        ],
    },
    {
        "name": "plastic",
        "metalness": 0,
        "roughness": 0.8,
        "transmission": 1,
        "ior": 1.531,
        "colors": [{"hsv": (0, 1, 1), "hue_variance": 360}],
    },
    {
        "name": "sand",
        "metalness": 0,
        "transmission": 0,
        "ior": 1.5,
        "colors": [{"hsv": (0.12360446570972887, 0.475, 0.44), "hue_variance": 5}],
    },
    {
        "name": "rubber",
        "metalness": 0,
        "transmission": 0,
        "ior": 1.5,
        "colors": [{"hsv": (0, 0, 0.023), "hue_variance": 360}],
    },
]

max_stats_roll = 0.0000013  # would be ~489,707 stat points

height_range_cm = (17, 60)  # 6 inches ~ 2 feet
extra_height_minimum = (
    height_range_cm[1] - height_range_cm[1] * 0.01
)  # 99% of max height must be reached to trigger extra height
extra_height_range_cm = (120, 240)  # 4 ~ 8 feet

weight_range_grams = (450, 1800)  # 1 ~ 4 pounds
extra_weight_range_grams = (3600, 7200)  # 8 ~ 15 pounds
weight_variance = (0.925, 1.075)  # +/-7.5% weight variance range

SIGNED_INT32_MAX = 2**31 - 1
SIGNED_INT32_MIN = -(2**31)


if settings().use_s3:
    s3 = boto3.Session(profile_name=settings().aws_profile).client("s3")


def resolve_color(c):
    return _color_generator.ryb_shift(
        *c["hsv"],
        random.randrange(
            -c["hue_variance"],
            c["hue_variance"],
        ),
    )


def resolve_basic_color_material(c):
    if random.random() <= 0.01:
        metalness = random.uniform(0.3, 1)
    else:
        metalness = 0

    if random.random() <= 0.01:
        transmission = random.uniform(0.2, 0.9)
    else:
        transmission = 0

    # 1% chance for metallic or transmissive material
    # but only allow one or the other
    # roll both to avoid metal appearing more often than transmissive
    if transmission > 0 and metalness > 0:
        if random.random() > 0.5:
            transmission = 0
        else:
            metalness = 0

    return {
        "name": "custom",
        "metalness": metalness,
        "roughness": 0 if metalness > 0 else 1,
        "transmission": transmission,
        "opacity": 0 if transmission > 0 else 1,
        "thickness": 0,
        "ior": random.uniform(1.3, 2),
        "color": c,
    }


def resolve_material(m):
    resolved_mat = {
        "name": m["name"],
        "metalness": m["metalness"],
        "transmission": m["transmission"],
        "opacity": 0 if m["transmission"] > 0 else 1,
        "thickness": m.get("thickness", 0),
        "ior": m["ior"],
        "color": resolve_color(random.choice(m["colors"])),
    }
    try:
        resolved_mat["roughness"] = m["roughness"]
    except KeyError:
        resolved_mat["roughness"] = 0 if m["metalness"] == 1 else 1

    return resolved_mat


def generate(unique_key: str):
    modifier = random.choice(modifiers)
    baller_name = random.choice(names)
    appraisal = random.choice(appraisals)

    roll = random.random()  # lower = better

    height_roll = random.random()
    height_cm = height_range_cm[0] + height_roll * (
        height_range_cm[1] - height_range_cm[0]
    )  # value should be uniform random between height_range_cm values
    if height_cm >= extra_height_minimum:
        # if roll is >= 99% of max regular height, roll extra height + weight
        height_cm = extra_height_range_cm[0] + height_roll * (
            extra_height_range_cm[1] - extra_height_range_cm[0]
        )
        weight_grams = extra_weight_range_grams[0] + height_roll * (
            extra_weight_range_grams[1] - extra_weight_range_grams[0]
        ) * random.uniform(weight_variance[0], weight_variance[1])
    else:
        weight_grams = weight_range_grams[0] + height_roll * (
            weight_range_grams[1] - weight_range_grams[0]
        ) * random.uniform(weight_variance[0], weight_variance[1])

    # find the correct rarity name to match the roll
    next_rarity_value = max_stats_roll
    rarity_name = rarity_names[0]
    for name_, req_value in rarity_table.items():
        if roll <= req_value:
            rarity_name = name_
            break
        else:
            next_rarity_value = req_value
    rarity_index = rarity_names.index(rarity_name)  # lazy

    # roll can be lower than max_rarity value (1.3 out of 1 million rolls)
    stats_roll = random.uniform(next_rarity_value, roll)

    #  approaches infinity at 0, reaches 0 at 1
    points = math.tan((1 - stats_roll) * (math.pi / 2))

    skill_points_to_distribute = round(points)

    stat_names = ["VIT", "END", "STR", "DEX", "RES", "INT", "FAI"]
    random.shuffle(stat_names)

    # max percentage ranges from an equal share
    # to 75% of remaining stat points
    max_pct_to_take = random.uniform(1 / len(stat_names), 0.75)

    base_stats = {}
    for stat in stat_names:
        # roll for actual percentage to take and calculate points
        points_to_take = round(
            random.uniform(0, max_pct_to_take) * skill_points_to_distribute
        )
        # clamp from 1 to 99
        base_stats[stat] = min(99, max(1, points_to_take))
        skill_points_to_distribute -= points_to_take

    # distrbute any leftover points to a random skill
    if skill_points_to_distribute > 0:
        stat_name = random.choice(stat_names)
        base_stats[stat_name] = min(
            99, base_stats[stat_name] + skill_points_to_distribute
        )

    item_count = 0
    item_rarity = 0.1
    # 10% chance of item, multiple item chance / 2 each time
    while random.random() <= item_rarity:
        item_rarity /= 2
        item_count += 1

    if item_count > SIGNED_INT32_MAX:
        item_count = SIGNED_INT32_MAX

    eye_count = 2
    while random.random() <= 0.3:
        eye_count += 1

    # 1/10,000 chance for 0 or 1 eyes
    # probability of 10+ eyes is < 1/10,000
    # so skip this in case of 10+ eyes
    if eye_count < 10 and random.random() <= 0.0001:
        eye_count = random.choice((0, 1))

    if eye_count > SIGNED_INT32_MAX:
        eye_count = SIGNED_INT32_MAX

    has_headwear = random.choice([True, False])

    if rarity_index < 3:  # Under sublime
        # 70% chance to get a generated color scheme
        use_color_scheme = random.random() <= 0.7
    else:
        use_color_scheme = False

    # 10% chance of multicolored eyes, 50% for items
    multicolored_eyes = random.random() <= 0.1
    multicolored_items = random.random() > 0.5

    if use_color_scheme:
        # determine how many colors are required
        material_count = 1
        if eye_count > 0:
            material_count += 1
        if item_count > 0:
            material_count += 1
        if has_headwear:
            material_count += 1

        # Weighted probability for different color schemes
        if material_count == 1:
            style_choices = ["monochrome"]
            weights = [100]
        elif material_count == 2:
            style_choices = ["monochrome", "complementary", "random"]
            weights = [49, 49, 2]
        elif material_count == 3:
            style_choices = [
                "monochrome",
                "complementary",
                "adjacent",
                "triad",
                "random",
            ]
            weights = [14, 14, 35, 35, 2]
        else:  # >= 4
            style_choices = [
                "monochrome",
                "complementary",
                "adjacent",
                "triad",
                "tetrad",
                "random",
            ]
            weights = [4, 4, 10, 10, 70, 2]
        chosen_style = random.choices(style_choices, weights=weights, k=1)[0]

        if chosen_style == "random":
            resolved_body_material = resolve_basic_color_material(
                _color_generator.random_color()
            )

            if has_headwear:
                resolved_headwear_material = resolve_basic_color_material(
                    _color_generator.random_color()
                )
            else:
                resolved_headwear_material = None

            if multicolored_eyes:
                resolved_eye_materials = [
                    resolve_basic_color_material(_color_generator.random_color())
                    for _ in range(eye_count)
                ]
            else:
                resolved_eye_materials = [
                    resolve_basic_color_material(_color_generator.random_color())
                ]

            if multicolored_items:
                resolved_item_materials = [
                    resolve_basic_color_material(_color_generator.random_color())
                    for _ in range(item_count)
                ]
            else:
                resolved_item_materials = [
                    resolve_basic_color_material(_color_generator.random_color())
                ]
        else:
            base_color = _color_generator.random_color()
            palette = [base_color]
            if chosen_style == "tetrad":
                palette.extend(_color_generator.generate_tetrad(*base_color))
            elif chosen_style == "triad":
                palette.extend(_color_generator.generate_triad(*base_color))
            elif chosen_style == "adjacent":
                palette.extend(_color_generator.generate_adjacent(*base_color))
            elif chosen_style == "complementary":
                palette.extend(
                    _color_generator.generate_adjacent(*base_color, degrees=180)
                )

            resolved_body_material = resolve_basic_color_material(palette[0])
            palette_index = 1 % len(palette)

            if eye_count > 0:
                eye_color = palette[palette_index]
                palette_index = (palette_index + 1) % len(palette)
                eye_shades = _color_generator.generate_shades(
                    *eye_color, shade_pairs=eye_count // 2
                )
                # len(eye_shades) will always be even
                # eye_shades.insert(len(eye_shades) // 2, eye_color)

                resolved_eye_materials = [
                    resolve_basic_color_material(eye_shades[a % len(eye_shades)])
                    for a in range(eye_count)
                ]
            else:
                resolved_eye_materials = []

            if item_count > 0:
                item_color = palette[palette_index]
                palette_index = (palette_index + 1) % len(palette)
                item_shades = _color_generator.generate_shades(
                    *item_color, shade_pairs=eye_count // 2
                )
                # len(item_shades) will always be even
                # item_shades.insert(len(item_shades) // 2, item_color)

                resolved_item_materials = [
                    resolve_basic_color_material(item_shades[a % len(item_shades)])
                    for a in range(item_count)
                ]
            else:
                resolved_item_materials = []

            if has_headwear:
                resolved_headwear_material = resolve_basic_color_material(
                    random.choice(
                        _color_generator.generate_shades(*palette[palette_index])
                    )
                )
            else:
                resolved_headwear_material = []

    else:
        allowed_materials = material_rarity_table[rarity_name]
        # 10% chance to upgrade material rarity
        # keep re-rolling on success
        for name in rarity_names[rarity_index:]:
            if random.random() <= 0.1:
                allowed_materials = material_rarity_table[name]
            else:
                break

        body_material = random.choice(allowed_materials)
        resolved_body_material = resolve_material(body_material)

        if has_headwear:
            headwear_material = random.choice(allowed_materials)
            resolved_headwear_material = resolve_material(headwear_material)
        else:
            resolved_headwear_material = None

        # allow lower-rarity materials for items / eyes
        for name in rarity_names:
            if name == rarity_name:
                break
            allowed_materials.extend(material_rarity_table[name])

        if eye_count > 0:
            if multicolored_eyes:
                eye_materials = random.choices(
                    allowed_materials,
                    k=eye_count,  # pyright: ignore [reportGeneralTypeIssues]
                )
            else:
                eye_materials = [random.choice(allowed_materials)]
        else:
            eye_materials = []

        resolved_eye_materials = []
        for mat in eye_materials:
            resolved_eye_materials.append(resolve_material(mat))

        if item_count > 0:
            if multicolored_items:
                item_materials = random.choices(
                    allowed_materials,
                    k=item_count,  # pyright: ignore [reportGeneralTypeIssues]
                )
            else:
                item_materials = [random.choice(allowed_materials)]
        else:
            item_materials = []

        resolved_item_materials = []
        for mat in item_materials:
            resolved_item_materials.append(resolve_material(mat))

    baller_filename = f"baller_{unique_key}.glb"
    export_path = Path(settings().base_baller_output_path, baller_filename)
    _blender_generator.generate_baller(
        export_path=export_path,
        seed=random.randrange(
            SIGNED_INT32_MIN, SIGNED_INT32_MAX
        ),  # Blender-defined min/max
        height=height_cm / 100,
        weight=weight_grams,
        body_noise=random.choice([True, False]),
        headwear=has_headwear,
        item_count=item_count,
        eye_count=eye_count,
    )

    if settings().use_s3:
        s3_key = Path(settings().s3_bucket_prefix, baller_filename).as_posix()
        s3.upload_file(  # pyright: ignore [reportUnboundVariable]
            export_path.as_posix(), settings().s3_bucket_name, s3_key
        )

        export_path_str = f"{settings().cdn_prefix}/{baller_filename}"
    else:
        export_path_str = export_path.as_posix()

    return {
        "modifier": modifier,
        "name": baller_name,
        "appraisal": appraisal,
        "roll": roll,
        "rarity_name": rarity_name,
        "points": points,
        "base_stats": base_stats,
        "height_roll": height_roll,
        "height": height_cm,
        "weight": weight_grams,
        "body_material": resolved_body_material,
        "headwear_material": resolved_headwear_material,
        "eye_materials": resolved_eye_materials,
        "item_materials": resolved_item_materials,
        "export_path": export_path_str,
    }
