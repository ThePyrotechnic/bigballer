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
import time
from urllib.parse import urlencode
from uuid import uuid4
from typing_extensions import Annotated

from acouchbase.transactions import AttemptContext
from couchbase.exceptions import (
    DocumentNotFoundException,
)
from couchbase.options import TransactionQueryOptions
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Security, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import APIKeyCookie
import jwt
import requests

from bigballer_api.data import close_db, cluster, connect_db, get_scope
import bigballer_api.generator as roller
from bigballer_api.models import (
    ItemsQuery,
    TradeQuery,
    TradeRequest,
    TradeStatusUpdate,
)
from bigballer_api.settings import settings


api_key_cookie = APIKeyCookie(name="access_token", auto_error=True)


app = FastAPI(title="BigBaller API", description="", version="0.0.1")

app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", close_db)


with open(settings().public_key_filepath, "rb") as public_key_file:
    PUBLIC_KEY: RSAPublicKey = serialization.load_pem_public_key(
        public_key_file.read()
    )  # pyright: ignore [reportGeneralTypeIssues]

with open(settings().private_key_filepath, "rb") as private_key_file:
    PRIVATE_KEY: RSAPrivateKey = serialization.load_pem_private_key(
        private_key_file.read(), password=None
    )  # pyright: ignore [ reportGeneralTypeIssues]


async def check_api_key(api_key: str = Security(api_key_cookie)) -> str:
    try:
        return jwt.decode(api_key, PUBLIC_KEY, ["RS256"])
    except jwt.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/items", tags=["items"])
async def get_items(
    items_query: Annotated[ItemsQuery, Depends()], api_key=Depends(check_api_key)
):
    bigballer_scope = await get_scope()

    if items_query.user_id is not None:
        user_id = items_query.user_id

        # Only show private keys when user is looking at their own items
        if user_id == api_key["claimed_id"]:
            private_keys = ", trade_id"
        else:
            private_keys = ""
    else:
        user_id = api_key["claimed_id"]
        private_keys = ", trade_id"

    items = bigballer_scope.query(
        f"SELECT META().id, appraisal, modifier, name, rarity{private_keys} FROM items WHERE owner = $user_id OFFSET $offset LIMIT $limit",
        user_id=user_id,
        offset=items_query.offset,
        limit=items_query.limit,
    )

    return JSONResponse({"items": [i async for i in items.rows()]})


@app.post("/roll", tags=["items"])
async def post_roll(pack: bool = False, api_key=Depends(check_api_key)):
    bigballer_scope = await get_scope()
    col_users = bigballer_scope.collection("users")
    col_items = bigballer_scope.collection("items")

    exception = None

    rolls = {}

    async def tx(context: AttemptContext):
        nonlocal exception, rolls

        try:
            user_query = await context.get(col_users, api_key["claimed_id"])
        except DocumentNotFoundException:  # New user
            if pack:
                exception = HTTPException(status.HTTP_404_NOT_FOUND)
                return

            res = requests.get(
                "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/",
                params={
                    "key": settings().steam_api_key,
                    "steamids": api_key["claimed_id"].rsplit("/", 1)[1],
                },
            )
            try:
                res.raise_for_status()
                steam_summary = res.json()["response"]["players"][0]
            except requests.exceptions.HTTPError:
                exception = HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to locate steam account",
                )
                return
            except requests.exceptions.JSONDecodeError:
                exception = HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Bad response from steam account service. Steam may be down",
                )
                return

            item_id = str(uuid4())
            creation_time = round(time.time() * 1000)
            roll = roller.generate(item_id)
            roll["owner"] = api_key["claimed_id"]
            roll["creation_time"] = creation_time

            await context.insert(
                col_users,
                api_key["claimed_id"],
                {
                    "items": [item_id],
                    "creation_time": creation_time,
                    "last_pinecone_time": creation_time,
                    "pinecones": settings().starting_pinecones,
                    "steam_personaname": steam_summary["personaname"],
                    "steam_steamid": steam_summary["steamid"],
                    "steam_profileurl": steam_summary["profileurl"],
                    "steam_avatar": steam_summary["avatar"],
                    "steam_avatarmedium": steam_summary["avatarmedium"],
                    "steam_avatarfull": steam_summary["avatarfull"],
                },
            )
            await context.insert(col_items, item_id, roll)
            rolls = {item_id: roll}
        else:
            user = user_query.content_as[dict]

            if pack:
                num_rolls = settings().rolls_per_pack
                cost = settings().pack_roll_cost
            else:
                num_rolls = 1
                cost = settings().roll_cost

            if user["pinecones"] < cost:
                exception = HTTPException(
                    status.HTTP_400_BAD_REQUEST, detail="Insufficient pinecones"
                )
                return
            creation_time = round(time.time() * 1000)  # Unix milliseconds
            for _ in range(num_rolls):
                item_id = str(uuid4())
                roll = roller.generate(item_id)
                roll["owner"] = api_key["claimed_id"]
                roll["creation_time"] = creation_time

                rolls[item_id] = roll

            user["items"].extend(list(rolls.keys()))
            user["pinecones"] -= cost

            await context.replace(user_query, user)

            for key, roll in rolls.items():
                await context.insert(col_items, key, roll)

    await cluster().transactions.run(tx)  # pyright: ignore [reportGeneralTypeIssues]

    if exception is not None:
        raise exception  # pyright: ignore [reportGeneralTypeIssues]

    return JSONResponse(rolls)


@app.get("/trades", tags=["trades"])
async def get_trades(
    trade_query: Annotated[TradeQuery, Depends()], api_key=Depends(check_api_key)
):
    status_filter = (
        f"AND status = '{trade_query.status}'" if trade_query.status is not None else ""
    )

    bigballer_scope = await get_scope()

    trades_query = bigballer_scope.query(
        f"SELECT META().id, status, sender_id, recipient_id FROM trades WHERE sender_id = $user_id {status_filter} ORDER BY creation_time OFFSET $offset LIMIT $limit",
        user_id=api_key["claimed_id"],
        offset=trade_query.offset,
        limit=trade_query.limit,
    )

    return JSONResponse([t async for t in trades_query.rows()])


@app.get("/trade/{trade_id}", tags=["trades"])
async def get_trade(trade_id: str, api_key=Depends(check_api_key)):
    bigballer_scope = await get_scope()
    col_trades = bigballer_scope.collection("trades")

    try:
        trade_query = await col_trades.get(trade_id)
    except DocumentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    trade = trade_query.content_as[dict]

    if trade["sender_id"] != api_key["claimed_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return JSONResponse(content=trade)


@app.post("/trade/{trade_id}", tags=["trades"])
async def post_trade_status(
    trade_id: str,
    status_update: TradeStatusUpdate,
    api_key=Depends(check_api_key),
):
    bigballer_scope = await get_scope()
    col_users = bigballer_scope.collection("users")
    col_trades = bigballer_scope.collection("trades")

    try:
        trade_query = await col_trades.get(trade_id)
    except DocumentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    trade = trade_query.content_as[dict]

    if trade["status"] != "sent":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a trade that is not pending",
        )

    if status_update.new_status == "accept":
        if api_key["claimed_id"] != trade["recipient_id"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        async def tx(context: AttemptContext):
            context.query(
                "UPDATE bigballer.bigballer.items USE KEYS $trade_items UNSET trade_id",
                TransactionQueryOptions(
                    named_parameters={
                        "trade_items": trade["sender_items"],
                        "trade_id": trade_id,
                    }
                ),
            )

            sender_query = await context.get(col_users, trade["sender_id"])
            sender = sender_query.content_as[dict]

            recipient_query = await context.get(col_users, trade["recipient_id"])
            recipient = recipient_query.content_as[dict]

            if len(trade["sender_items"]) > 0:
                sender_set = set(trade["sender_items"])
                sender["items"] = [i for i in sender["items"] if i not in sender_set]

                recipient["items"].extend(trade["sender_items"])

            if len(trade["recipient_items"]) > 0:
                recipient_set = set(trade["recipient_items"])
                recipient["items"] = [
                    i for i in recipient["items"] if i not in recipient_set
                ]

                sender["items"].extend(trade["sender_items"])

        await cluster().transactions.run(
            tx  # pyright: ignore [reportGeneralTypeIssues]
        )
    else:
        if (
            status_update.new_status == "reject"
            and api_key["claimed_id"] != trade["recipient_id"]
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if (
            status_update.new_status == "cancel"
            and api_key["claimed_id"] != trade["sender_id"]
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        async def tx(context: AttemptContext):
            context.query(
                "UPDATE bigballer.bigballer.items USE KEYS $trade_items UNSET trade_id",
                TransactionQueryOptions(
                    named_parameters={
                        "trade_items": list(trade["sender_items"]),
                        "trade_id": trade_id,
                    }
                ),
            )

            trade["status"] = (
                "rejected" if status_update.new_status == "reject" else "cancelled"
            )
            trade_query = await context.get(col_trades, trade_id)
            await context.replace(trade_query, trade)

    await cluster().transactions.run(tx)  # pyright: ignore [reportGeneralTypeIssues]


@app.post("/trade", tags=["trades"])
async def post_new_trade(trade_request: TradeRequest, api_key=Depends(check_api_key)):
    if trade_request.recipient_id == api_key["claimed_id"]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Sender and recipient cannot be the same"
        )

    if len(trade_request.sender_items) == 0 or len(trade_request.recipient_items) == 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Trade must involve at least 1 item"
        )

    bigballer_scope = await get_scope()
    col_users = bigballer_scope.collection("users")

    try:
        await col_users.get(trade_request.recipient_id)
    except DocumentNotFoundException:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Recipient does not exist")

    trade_items = list(trade_request.sender_items.union(trade_request.recipient_items))

    items_query = bigballer_scope.query(
        "SELECT META().id, owner, trade_id FROM items WHERE META().id IN $ids",
        ids=trade_items,
    )

    found_items = {api_key["claimed_id"]: set(), trade_request.recipient_id: set()}
    async for item in items_query.rows():
        if item.get("trade_id"):
            if item["owner"] == api_key["claimed_id"]:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED
                )  # Item is already in a trade

        found_items[item["owner"]].add(item["id"])

    if (
        found_items[api_key["claimed_id"]] != trade_request.sender_items
        or found_items[trade_request.recipient_id] != trade_request.recipient_items
    ):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED
        )  # All items must exist and have the correct owner

    col_users = bigballer_scope.collection("users")
    col_trades = bigballer_scope.collection("trades")

    trade_id = str(uuid4())

    trade = {
        "sender_id": api_key["claimed_id"],
        "recipient_id": trade_request.recipient_id,
        "sender_items": list(trade_request.sender_items),
        "recipient_items": list(trade_request.recipient_items),
        "creation_time": round(time.time() * 1000),  # Unix milliseconds
        "status": "sent",
    }

    async def tx(context: AttemptContext):
        context.query(
            "UPDATE bigballer.bigballer.items USE KEYS $trade_items SET trade_id = $trade_id",
            TransactionQueryOptions(
                named_parameters={
                    "trade_items": list(trade_request.sender_items),
                    "trade_id": trade_id,
                }
            ),
        )

        # Add trade to both users
        for user_id in [api_key["claimed_id"], trade_request.recipient_id]:
            user_query = await context.get(col_users, user_id)
            user = user_query.content_as[dict]

            try:
                user["trades"].append(trade_id)
            except KeyError:
                user["trades"] = [trade_id]

            await context.replace(user_query, user)

        await context.insert(col_trades, trade_id, trade)

    await cluster().transactions.run(tx)  # pyright: ignore [reportGeneralTypeIssues]


@app.post("/pinecones", tags=["users"])
async def post_pinecones(api_key=Depends(check_api_key)):
    bigballer_scope = await get_scope()
    col_users = bigballer_scope.collection("users")

    exists = await col_users.exists(api_key["claimed_id"])
    if not exists.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    new_pinecones = 0
    total_pinecones = 0

    async def tx(context: AttemptContext):
        nonlocal new_pinecones, total_pinecones

        current_time = round(time.time() * 1000)

        user_query = await context.get(col_users, api_key["claimed_id"])
        user = user_query.content_as[dict]

        total_pinecones = user["pinecones"]

        time_delta = current_time - user["last_pinecone_time"]
        if time_delta > settings().pinecone_base_rate:
            # Number of elapsed periods since last update
            #  ex: if period is 5 minutes and 11 minutes have elapsed,
            #  then periods_delta == 2
            periods_delta = time_delta // settings().pinecone_base_rate

            new_pinecones = periods_delta * settings().pinecone_base_amount
            total_pinecones = user["pinecones"] + new_pinecones
            user["pinecones"] = total_pinecones
            user["last_pinecone_time"] = current_time

            await context.replace(user_query, user)

    await cluster().transactions.run(tx)  # pyright: ignore [reportGeneralTypeIssues]

    return JSONResponse(
        {"new_pinecones": new_pinecones, "total_pinecones": total_pinecones}
    )


@app.get("/users", tags=["users"])
async def get_users(
    like: str = Query(regex=r"^[^\% \\]{3,64}$"), _=Depends(check_api_key)
):
    like = like + "%"

    bigballer_scope = await get_scope()

    users_query = bigballer_scope.query(
        "SELECT META().id, steam_personaname, steam_avatarmedium FROM users WHERE LOWER(steam_personaname) LIKE LOWER($like) LIMIT $limit",
        like=like,
        limit=5,
    )

    return JSONResponse([t async for t in users_query.rows()])


# Partially adapted from: https://github.com/xamey/steam-openid-fastapi/
#  Also see:
#  https://stackoverflow.com/questions/53573820/steam-openid-signature-validation
@app.get("/login", tags=["login"])
async def get_login():
    steam_params = urlencode(
        {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": settings().oid_redirect,
            "openid.realm": settings().oid_redirect,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
    )

    return RedirectResponse(
        url=f"{settings().oid_endpoint}?{steam_params}",
        status_code=status.HTTP_303_SEE_OTHER,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


@app.get("/loginResponse", tags=["login"])
async def get_login_response(request: Request):
    validation_params = {
        "openid.ns": request.query_params["openid.ns"],
        "openid.mode": "check_authentication",
        "openid.op_endpoint": request.query_params["openid.op_endpoint"],
        "openid.claimed_id": request.query_params["openid.claimed_id"],
        "openid.identity": request.query_params["openid.identity"],
        "openid.return_to": request.query_params["openid.return_to"],
        "openid.response_nonce": request.query_params["openid.response_nonce"],
        "openid.assoc_handle": request.query_params["openid.assoc_handle"],
        "openid.signed": request.query_params["openid.signed"],
        "openid.sig": request.query_params["openid.sig"],
    }
    res = requests.get(str(settings().oid_endpoint), params=validation_params)

    try:
        res.raise_for_status()
        if not res.text == "ns:http://specs.openid.net/auth/2.0\nis_valid:true\n":
            raise ValueError
    except (requests.HTTPError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = jwt.encode(
        {"claimed_id": request.query_params["openid.claimed_id"]},
        key=PRIVATE_KEY,
        algorithm="RS256",
    )

    response = RedirectResponse(
        url=str(settings().website_url), status_code=status.HTTP_303_SEE_OTHER
    )

    response.set_cookie(
        key="access_token",
        value=token,
        expires=60 * 60 * 24 * 30,  # 1 month
        secure=True,
        httponly=False,
        samesite="strict",
    )

    return response
