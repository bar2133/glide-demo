from pydantic import BaseModel
from datetime import datetime


class JWTTokenResponse(BaseModel):
    """Response model for JWT token generation.

    This model represents the response containing the generated JWT token
    and metadata about its creation.
    """
    token: str
    created_at: datetime
    expires_at: datetime
    algorithm: str
