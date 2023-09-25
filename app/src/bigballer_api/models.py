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
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Item(BaseModel):
    pass


class User(BaseModel):
    pass


class ItemsQuery(BaseModel):
    user_id: str | None = Field(min_length=38, max_length=64)
    limit: int = Field(10, gt=0, le=20)
    offset: int = Field(0, ge=0)


class TradeQuery(ItemsQuery):
    status: Literal["sent", "completed", "cancelled", "rejected"] | None


class TradeRequest(BaseModel):
    recipient_id: str
    sender_items: set
    recipient_items: set

    @field_validator("sender_items", "recipient_items")
    @classmethod
    def max_items_length(cls, v: set) -> set:
        max_len = 10
        if len(v) > max_len:
            raise ValueError(f"Must not contain more than {max_len} items")
        return v


class TradeStatusUpdate(BaseModel):
    new_status: Literal["reject", "accept", "cancel"]


class Trade(TradeRequest):
    sender_id: str
    creation_time: datetime
    status: Literal["sent", "completed", "cancelled", "rejected"]
