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
import random

from bigballer_api.generator._words import modifiers, names, appraisals


rarity_table = {
    "transcendant": 1 / 391,
    "sublime": 1 / 156,
    "pristine": 1 / 31.3,
    "notable": 1 / 6.26,
    # "common": 1 / 1.25,
}
lowest_rarity_name = "common"

max_stats_roll = 0.0000013  # ~489,707


height_range_cm = (15, 60)  # 6 inches ~ 2 feet
extra_height_minimum = (
    height_range_cm[1] - height_range_cm[1] * 0.01
)  # 1% of max height
extra_height_range_cm = (120, 240)  # 4 ~ 8 feet

weight_range_grams = (450, 1800)  # 1 ~ 4 pounds
extra_weight_range_grams = (3600, 7200)  # 8 ~ 15 pounds
weight_variance = (-0.075, 0.075)  # up to 15% weight variance


def generate():
    modifier = random.choice(modifiers)
    name = random.choice(names)
    appraisal = random.choice(appraisals)

    roll = random.random()

    height_roll = random.random()
    height_cm = height_range_cm[0] + height_roll * height_range_cm[1]
    if height_cm >= extra_height_minimum:
        height_cm = extra_height_range_cm[0] + height_roll * extra_height_range_cm[1]
        weight_grams = extra_weight_range_grams[
            0
        ] + height_roll * extra_weight_range_grams[1] * random.uniform(
            weight_variance[0], weight_variance[1]
        )
    else:
        weight_grams = weight_range_grams[0] + height_roll * weight_range_grams[
            1
        ] * random.uniform(weight_variance[0], weight_variance[1])

    next_rarity_value = max_stats_roll
    rarity_name = lowest_rarity_name
    for name_, req_value in rarity_table.items():
        if roll <= req_value:
            rarity_name = name_
            break
        else:
            next_rarity_value = req_value

    stats_roll = random.uniform(next_rarity_value, roll)

    points = math.tan((1 - stats_roll) * (math.pi / 2))

    skill_points_to_distribute = round(points)

    stat_names = ["VIT", "END", "STR", "DEX", "RES", "INT", "FAI"]
    random.shuffle(stat_names)

    base_stats = {}
    for stat in stat_names:
        max_pct_to_take = random.uniform(1 / len(stat_names), 0.75)
        points_to_take = round(
            random.uniform(0, max_pct_to_take) * skill_points_to_distribute
        )
        base_stats[stat] = min(99, max(1, points_to_take))
        skill_points_to_distribute -= points_to_take

    if skill_points_to_distribute > 0:
        stat_name = random.choice(stat_names)
        base_stats[stat_name] = min(
            99, base_stats[stat_name] + skill_points_to_distribute
        )

    return {
        "modifier": modifier,
        "name": name,
        "appraisal": appraisal,
        "roll": roll,
        "rarity_name": rarity_name,
        "points": points,
        "base_stats": base_stats,
        "height_roll": height_roll,
        "height": height_cm,
        "weight": weight_grams,
    }
