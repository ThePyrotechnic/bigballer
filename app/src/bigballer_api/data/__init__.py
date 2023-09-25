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
from acouchbase.bucket import Bucket, Scope
from acouchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions

from bigballer_api.settings import settings


_cluster: Cluster = None


def cluster() -> Cluster:
    return _cluster


async def get_scope() -> Scope:
    bucket: Bucket = _cluster.bucket("bigballer")
    await bucket.on_connect()
    return bucket.scope("bigballer")


async def connect_db():
    global _cluster

    _cluster = await Cluster.connect(
        str(settings().db_url),
        ClusterOptions(
            PasswordAuthenticator(settings().db_username, settings().db_password)
        ),
    )


async def close_db():
    await _cluster.close()
