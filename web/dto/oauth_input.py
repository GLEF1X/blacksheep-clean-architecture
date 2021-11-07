from pydantic import BaseModel


class OauthFormInput(BaseModel):
    username: str
    password: str
