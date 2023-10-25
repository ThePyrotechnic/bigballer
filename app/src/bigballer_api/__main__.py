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
import uvicorn

# Leave this import in to explicitly "link" bigballer_api:app
#   to this file in the import tree. Just in case
from bigballer_api import app  # noqa: F401 # pyright: ignore
from bigballer_api.settings import settings


def main():
    uvicorn.run(
        "bigballer_api:app",
        host=settings().host,
        port=settings().port,
        reload=settings().hot_reload,
    )


print(__name__)
if __name__ == "__main__":
    main()
