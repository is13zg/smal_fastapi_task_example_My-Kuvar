from typing import Annotated

from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationInfo, model_validator



STR_20 = Annotated[str, Field(..., max_length=20)]
PASSWORD = Annotated[str, Field(..., min_length=6, max_length=30)]
STR_20_OP = Annotated[str | None, Field(max_length=20, default=None)]
PASSWORD_OP = Annotated[str | None, Field(min_length=6, max_length=30, default=None)]



class UserLogin(BaseModel):
    email: EmailStr
    passwd: PASSWORD

    @classmethod
    @field_validator("email")
    def lower_email(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return v.strip().lower()


class UserRegister(UserLogin):
    name: STR_20
    last_name: STR_20
    father_name: STR_20
    rep_passwd: PASSWORD

    @classmethod
    @field_validator("rep_passwd")
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if "passwd" in info.data and v != info.data["passwd"]:
            raise ValueError("passwords do not match")
        return v


class UserUpdate(UserRegister):
    email: EmailStr = Field(default=None)
    passwd: PASSWORD_OP
    name: STR_20_OP
    last_name: STR_20_OP
    father_name: STR_20_OP
    rep_passwd: PASSWORD_OP

    @field_validator("passwd", "rep_passwd", mode="before")
    @classmethod
    def _normalize(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        return v if v != "" else None

    @model_validator(mode="after")
    def passwords_match(self):

        if (self.passwd is None) ^ (self.rep_passwd is None):
            raise ValueError("Need passwd and rep_passwd")

        if self.passwd is not None and self.passwd != self.rep_passwd:
            raise ValueError("passwords do not match")
        return self


class UserOut(BaseModel):
    id: int
    name: str



class ExtUserOut(UserOut):
    email: EmailStr
    last_name: STR_20_OP
    father_name: STR_20_OP


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
