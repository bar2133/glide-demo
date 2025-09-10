from pydantic import BaseModel, field_validator
from common_components.models.oauth_enums import GrantType
from typing import Optional
from datetime import datetime


class TokenDTO(BaseModel):
    """OAuth token response model.

    Represents an OAuth token response with access token and optional grant type.
    """

    access_token: str
    grant_type: Optional[GrantType] = None
    token_type: str = "Bearer"
    iat: datetime
    exp: datetime

    @field_validator("access_token")
    @staticmethod
    def validate_access_token(v: str) -> str:
        """Validate that access token is not empty.

        Args:
            v: The access token value to validate.

        Returns:
            The validated access token.

        Raises:
            ValueError: If access token is empty.
        """
        if not len(v):
            raise ValueError("Access token cannot be empty")
        return v
