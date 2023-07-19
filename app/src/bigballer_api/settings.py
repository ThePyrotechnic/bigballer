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

from pydantic import BaseSettings, AnyUrl


@lru_cache
def settings():
    return _Settings()


class _Settings(BaseSettings):
    public_key_filepath: str
    private_key_filepath: str
    oid_endpoint: AnyUrl = "https://steamcommunity.com/openid/login"
    oid_redirect: AnyUrl = "http://localhost:1234/api/loginResponse"
    website_url: AnyUrl = "http://localhost:1234"
    host: str = "0.0.0.0"
    port: int = 8000
    db_url: AnyUrl
    db_username: str
    db_password: str
    steam_api_key: str
    starting_pinecones: int = 4000
    pinecone_base_amount: int = 2  # per base rate
    pinecone_base_rate: int = 300000  # milliseconds
    roll_cost: int = 1000
    pack_roll_cost: int = 4000
    rolls_per_pack = 5

    class Config:
        if os.environ.get("BIGBALLER_ENV_FILE"):
            env_file = os.environ["BIGBALLER_ENV_FILE"]
            env_file_encoding = "utf-8"
