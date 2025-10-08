from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, text, func
import hashlib
import re
from sqlalchemy.orm import declared_attr
from humps import camel
from typing import Type
from pydantic import BaseModel as PydanticBaseModel

class BaseModel(SQLModel, table=False):
    __abstract__ = True

    class Config:
        alias_generator = camel.case
        populate_by_name = True

    id:int = Field(default=None, primary_key=True)
    create_time:datetime = Field(
        default=None, sa_column_kwargs={"nullable": False, "server_default": text(str(func.current_timestamp())), "comment": "数据创建时间"}
    )

    update_time:datetime = Field(
        default=None,
        sa_column_kwargs={
            "nullable": False,
            "server_default": text(
                " ON UPDATE ".join([str(func.current_timestamp())] * 2)
            ),
            "comment": "数据更新时间",
        },
    )

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.id != 0 and self.id == o.id

    def __hash__(self) -> int:
        return int(hashlib.md5(f"{self.__class__.__name__}:{self.id}".encode()).hexdigest(), 16)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        if cls.__name__[-5:] != "Model":
            raise ValueError("model class name should end up with Model")
        name_list = re.findall(r"[A-Z][a-z\d]*", cls.__name__)[:-1]
        return "_".join(name_list).lower()