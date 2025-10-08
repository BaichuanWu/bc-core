from pydantic import BaseModel, ConfigDict
from humps import camel

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=camel.case,
        populate_by_name=True,
        json_encoders={
        },
        from_attributes=True,
    )
