from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác kế thừa"""
    model_config = ConfigDict(from_attributes=True)
