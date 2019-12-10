from typing import Any, Optional, List, Dict

from pydantic import BaseModel, validator, Field


class Auth(BaseModel):
    token: Optional[str] = None
    user: Optional[str] = None
    passwd: Optional[str] = None

    @validator('token', always=True)
    def check_token_or_user_passwd(cls, token, values):
        if not token and (not values.get('user', False) or not values.get('passwd', False)):
            raise ValueError('Either token or user and password is required in the auth object.')
        return token


class SaveStateSchema(BaseModel):
    state: Any
    service: str


class RequestStateAccessSchema(BaseModel):
    auth: Auth


class Descriptor(BaseModel):
    items: Dict = Field(..., min_properties=1)


class CreateDataSchema(BaseModel):
    service: str
    auth: Auth
    descriptors: List[Dict] = Field(..., min_items=1, min_properties=1)


class CreateTaskSchema(BaseModel):
    task_name: str = Field(..., min_length=5)
    args: Dict = Field(..., min_properties=1)
