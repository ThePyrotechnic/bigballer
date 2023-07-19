// bigballer web - collect items
//     Copyright (C) 2023  Michael Manis - michaelmanis@tutanota.com
//     This program is free software: you can redistribute it and/or modify
//     it under the terms of the GNU Affero General Public License as published
//     by the Free Software Foundation, either version 3 of the License, or
//     (at your option) any later version.
//     This program is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU Affero General Public License for more details.
//     You should have received a copy of the GNU Affero General Public License
//     along with this program.  If not, see <https://www.gnu.org/licenses/>.
const accessToken = document.cookie.split("; ")
    .find((row) => row.startsWith("access_token="))?.split("=")[1];

const vowels = new Set(["a", "e", "i", "o", "u"]);

const getItems = async () => {
    const userId = document.getElementById("i-user-id-items").value;

    const res = await fetch("/api/items?" + new URLSearchParams({
        user_id: userId,
    }));
    const items = (await res.json()).items;

    document.getElementById("p-items-result").innerHTML = JSON.stringify(items);
};

const getUsers = async () => {
    const searchKey = document.getElementById("i-user-search").value;

    const res = await fetch("/api/users?" + new URLSearchParams({
        like: searchKey,
    }));
    const users = (await res.json());

    document.getElementById("p-user-search-result").innerHTML = JSON.stringify(users);
};

const getMyTrades = async () => {
    const statusFilter = document.getElementById("select-trade-status").value;
    let url = "/api/trades"
    if (statusFilter !== "all") {
        url += "?" + new URLSearchParams({
            status: statusFilter,
        });
    }

    const res = await fetch(url);
    const trades = (await res.json());

    document.getElementById("p-trades-result").innerHTML = JSON.stringify(trades);
};

const getTrade = async () => {
    const tradeId = document.getElementById("i-trade-id").value;

    const res = await fetch(`/api/trade/${tradeId}`);
    const trades = (await res.json());

    document.getElementById("p-trade-details").innerHTML = JSON.stringify(trades);
};

const updateTrade = async () => {
    const tradeId = document.getElementById("i-trade-id").value;
    const newStatus = document.getElementById("select-update-trade-status").value;

    await fetch(`api/trade/${tradeId}`, {
        method: "POST",
        body: JSON.stringify({
            new_status: newStatus
        }),
        headers: {"Content-Type": "application/json"}
    });
};

const postTrade = async () => {
    const senderItems = document.getElementById("i-trade-own-items").value.split(",");
    const recipientId = document.getElementById("i-trade-recipient").value;
    const recipientItems = document.getElementById("i-trade-their-items").value.split(",");
    
    await fetch("/api/trade", {
            method: "POST",
            body: JSON.stringify({
                "sender_items": senderItems,
                "recipient_id": recipientId,
                "recipient_items": recipientItems
            }),
            headers: {"Content-Type": "application/json"}
    });
};

const postRoll = async (pack = false) => {
    const res = await fetch(
        "/api/roll" + "?" + new URLSearchParams(
            {pack: pack}
        ), 
        {method: "POST"}
    );
    const rolls = await res.json();
    document.getElementById("p-roll-result").innerHTML = JSON.stringify(rolls);

    postPinecones();
};

const postPinecones = async () => {
    if (!authenticated()) { return }

    const res = await fetch("/api/pinecones", {method: "POST"});
    const pinecones = await res.json();
    document.getElementById("p-pinecones").innerHTML = `${pinecones["total_pinecones"]} (+${pinecones["new_pinecones"]})`;
};

const authenticated = () => {
    return accessToken != null;
};

const login = () => {
    window.location = "/api/login";
};

const logout = () => {
    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.reload();
};

document.addEventListener('DOMContentLoaded', async () => {
    if (document.cookie.match(/^(.*;)?\s*access_token\s*=\s*[^;]+(.*)?$/)) {
        document.getElementById("btn-login").setAttribute("disabled", "");

    } else {
        document.getElementById("btn-logout").setAttribute("disabled", "");
        document.getElementById("btn-roll").setAttribute("disabled", "");
        document.getElementById("btn-my-items").setAttribute("disabled", "");
    }

    postPinecones();
    setInterval(postPinecones, 10000);
});
