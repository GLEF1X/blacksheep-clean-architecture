from typing import List

from pydantic import BaseModel


class OauthFormInput(BaseModel):
    username: str
    password: str
    scopes: List[str]
