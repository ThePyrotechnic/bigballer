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
