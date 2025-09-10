from pydantic import BaseModel


class TelcoAuthData(BaseModel):
    """Telco authentication data.
    """
    client_id: str
    client_secret: str
