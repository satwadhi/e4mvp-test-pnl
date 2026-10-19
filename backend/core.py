import os
from datetime import datetime
from typing import Annotated, Any, Optional
from zoneinfo import ZoneInfo

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

client = AsyncIOMotorClient(os.environ["MONGO_URL"], tz_aware=True)
db = client[os.environ["DB_NAME"]]

MUSCAT = ZoneInfo("Asia/Muscat")


def muscat_today():
    return datetime.now(MUSCAT).date()


PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


class BaseDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    @classmethod
    def from_mongo(cls, doc: dict):
        return cls.model_validate(doc)

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True)
        _id = data.pop("_id", None)
        if _id:
            data["_id"] = ObjectId(_id)
        return data


class User(BaseDocument):
    email: str
    password_hash: str
    name: str = "Admin"
    role: str = "admin"
    created_at: datetime


class Record(BaseDocument):
    category: str
    date: Optional[str] = None
    month: Optional[str] = None
    values: dict[str, Any]
    is_sample: bool = False
    created_at: datetime
    updated_at: datetime
