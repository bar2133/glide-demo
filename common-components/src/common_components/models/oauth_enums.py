"""OAuth-related enums for the application."""

from enum import StrEnum


class GrantType(StrEnum):
    """OAuth 2.0 grant type enumeration.

    Defines the standard OAuth 2.0 grant types as specified in RFC 6749.
    """

    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    PASSWORD = "password"
    REFRESH_TOKEN = "refresh_token"
    IMPLICIT = "implicit"
