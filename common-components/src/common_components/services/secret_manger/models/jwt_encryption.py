from pydantic import BaseModel


class JWTEncryptionData(BaseModel):
    key: str
    algo: str
    exp_sec: int
