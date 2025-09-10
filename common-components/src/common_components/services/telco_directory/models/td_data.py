from pydantic import BaseModel, ConfigDict


class SingleTelcoData(BaseModel):
    """Model for a single telco data.

    This model represents a single telco data with a base URL, client ID, and client secret.
    """
    model_config = ConfigDict(from_attributes=True, coerce_numbers_to_str=True)
    base_url: str
    client_id: str
    client_secret: str


class TDData(BaseModel):
    """Model for the Telco Directory data.

    This model represents the Telco Directory data with a dictionary of prefixes
    and their corresponding telco data.
    """
    model_config = ConfigDict(from_attributes=True, coerce_numbers_to_str=True)
    prefixes: dict[str, SingleTelcoData]
