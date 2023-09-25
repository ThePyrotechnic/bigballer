bigballer api - collect items

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


## Development
### Database
1. `docker run -t --name db -p 8091-8096:8091-8096 -p 11210-11211:11210-11211 couchbase/server:community-7.2.0`
1. (`docker start/stop db` for future runs)
### App Server
1. `cd app`
1. `pip install -e .[dev]`
1. `cd ..`
1. `$BIGBALLER_ENV_FILE=".env.local`
1. `make app`
### Web Server
1. `cd web`
1. `npm install .`
1. `cd ..`
1. `make web`
