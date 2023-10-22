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
from functools import lru_cache
import os

from pydantic import AnyHttpUrl, AnyUrl
from pydantic_settings import BaseSettings


@lru_cache
def settings():
    return _Settings()  # pyright: ignore [reportGeneralTypeIssues]


class _Settings(BaseSettings):
    aws_profile: str | None = None
    baller_generation_script_filepath: str
    base_baller_blend_filepath: str
    base_baller_output_path: str
    blender_binary_filepath: str
    cdn_prefix: str = ""
    db_password: str
    db_url: AnyUrl
    db_username: str
    host: str = "0.0.0.0"
    hot_reload: bool = False
    oid_endpoint: AnyHttpUrl = "https://steamcommunity.com/openid/login"  # pyright: ignore [reportGeneralTypeIssues] # noqa: E501
    oid_redirect: AnyHttpUrl = "http://localhost:1234/api/loginResponse"  # pyright: ignore [reportGeneralTypeIssues] # noqa: E501
    pack_roll_cost: int = 4000
    pinecone_base_amount: int = 2  # per base rate
    pinecone_base_rate: int = 300000  # milliseconds
    port: int = 8000
    private_key_filepath: str
    public_key_filepath: str
    roll_cost: int = 1000
    rolls_per_pack: int = 5
    s3_bucket_name: str = ""
    s3_bucket_prefix: str = ""
    starting_pinecones: int = 4000
    steam_api_key: str
    use_s3: bool = False
    website_url: AnyHttpUrl = (
        "http://localhost:1234"  # pyright: ignore [reportGeneralTypeIssues]
    )

    class Config:
        if os.environ.get("BIGBALLER_ENV_FILE"):
            env_file = os.environ["BIGBALLER_ENV_FILE"]
            env_file_encoding = "utf-8"
