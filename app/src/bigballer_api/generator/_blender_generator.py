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
from pathlib import Path
import subprocess

from bigballer_api.settings import settings


def generate_baller(
    export_path: Path,
    seed: int,
    height: float,
    weight: float,
    body_noise: bool,
    headwear: bool,
    item_count: int,
    eye_count: int,
):
    result = subprocess.run(
        [
            settings().blender_binary_filepath,
            settings().base_baller_blend_filepath,
            "--background",
            "--python",
            settings().baller_generation_script_filepath,
            "--",  # start of python script args
            export_path.resolve().as_posix(),
            str(seed),
            str(height),
            str(weight),
            str(body_noise),
            str(headwear),
            str(item_count),
            str(eye_count),
        ],
        capture_output=True,
    )

    print(result.stdout.decode("utf-8"))
