from pydantic import BaseModel


class TelcoAuthData(BaseModel):
    """Telco authentication data.
    """
    auth_client_certs: dict[str, str]
