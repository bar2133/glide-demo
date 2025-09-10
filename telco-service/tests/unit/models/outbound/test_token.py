"""Functional tests for OutboundToken model."""

import pytest
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError
from common_components.models.token import TokenDTO
from common_components.models.oauth_enums import GrantType


class TestOutboundToken:
    """Test class for OutboundToken model functionality."""

    def test_valid_outbound_token_creation(self) -> None:
        """Test creating a valid OutboundToken instance.

        Validates that an OutboundToken can be created with a valid access_token.
        """
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            iat=now,
            exp=now + timedelta(hours=1)
        )

        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

    def test_outbound_token_with_empty_string(self) -> None:
        """Test creating OutboundToken with empty string.

        Validates that empty access_token raises ValidationError.
        """
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError) as exc_info:
            TokenDTO(
                access_token="",
                iat=now,
                exp=now + timedelta(hours=1)
            )

        errors = exc_info.value.errors()
        # Should have validation error for empty access_token
        access_token_errors = [e for e in errors if e["loc"] == ("access_token",)]
        assert len(access_token_errors) == 1
        assert "Access token cannot be empty" in access_token_errors[0]["msg"]

    def test_outbound_token_with_long_token(self) -> None:
        """Test creating OutboundToken with a long JWT token.

        Validates that OutboundToken can handle long access tokens like JWT.
        """
        long_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        now = datetime.now(timezone.utc)

        token = TokenDTO(
            access_token=long_token,
            iat=now,
            exp=now + timedelta(hours=1)
        )

        assert token.access_token == long_token

    def test_outbound_token_required_field(self) -> None:
        """Test that access_token field is required.

        Validates that ValidationError is raised when access_token is not provided.
        """
        with pytest.raises(ValidationError) as exc_info:
            TokenDTO()  # type: ignore

        errors = exc_info.value.errors()
        # Should have 3 missing field errors: access_token, iat, exp
        assert len(errors) == 3
        missing_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        assert missing_fields == {"access_token", "iat", "exp"}

    def test_outbound_token_with_none(self) -> None:
        """Test OutboundToken with None value.

        Validates that None access_token raises ValidationError.
        """
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError) as exc_info:
            TokenDTO(
                access_token=None,  # type: ignore
                iat=now,
                exp=now + timedelta(hours=1)
            )

        errors = exc_info.value.errors()
        # Should have validation error for None access_token
        access_token_errors = [e for e in errors if e["loc"] == ("access_token",)]
        assert len(access_token_errors) == 1

    def test_outbound_token_with_numeric_input(self) -> None:
        """Test OutboundToken with numeric input.

        Validates that numeric values are converted to strings.
        """
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token="12345",
            iat=now,
            exp=now + timedelta(hours=1)
        )

        assert token.access_token == "12345"
        assert isinstance(token.access_token, str)

    def test_outbound_token_model_dump(self) -> None:
        """Test model serialization to dictionary.

        Validates that the model can be properly serialized to a dictionary.
        """
        now = datetime.now(timezone.utc)
        exp_time = now + timedelta(hours=1)
        token = TokenDTO(
            access_token="test_token_123",
            iat=now,
            exp=exp_time
        )
        data = token.model_dump()

        expected = {
            "access_token": "test_token_123",
            "grant_type": None,
            "token_type": "Bearer",
            "iat": now,
            "exp": exp_time
        }
        assert data == expected

    def test_outbound_token_model_dump_json(self) -> None:
        """Test model serialization to JSON.

        Validates that the model can be properly serialized to JSON string.
        """
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token="test_token_123",
            iat=now,
            exp=now + timedelta(hours=1)
        )
        json_str = token.model_dump_json()

        assert '"access_token":"test_token_123"' in json_str
        assert '"grant_type":null' in json_str
        assert '"token_type":"Bearer"' in json_str
        assert '"iat"' in json_str
        assert '"exp"' in json_str

    def test_outbound_token_from_dict(self) -> None:
        """Test model creation from dictionary.

        Validates that OutboundToken can be created from a dictionary.
        """
        now = datetime.now(timezone.utc)
        exp_time = now + timedelta(hours=1)
        data = {
            "access_token": "test_token_456",
            "iat": now,
            "exp": exp_time
        }
        token = TokenDTO(**data)

        assert token.access_token == "test_token_456"
        assert token.iat == now
        assert token.exp == exp_time

    def test_outbound_token_equality(self) -> None:
        """Test equality comparison between OutboundToken instances.

        Validates that two OutboundToken instances with same values are equal.
        """
        now = datetime.now(timezone.utc)
        exp_time = now + timedelta(hours=1)

        token1 = TokenDTO(
            access_token="test_token",
            iat=now,
            exp=exp_time
        )
        token2 = TokenDTO(
            access_token="test_token",
            iat=now,
            exp=exp_time
        )
        token3 = TokenDTO(
            access_token="different_token",
            iat=now,
            exp=exp_time
        )

        assert token1 == token2
        assert token1 != token3

    def test_outbound_token_repr_and_str(self) -> None:
        """Test string representation of OutboundToken.

        Validates that the model has proper string representation.
        """
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token="test_token_123",
            iat=now,
            exp=now + timedelta(hours=1)
        )

        repr_str = repr(token)
        str_str = str(token)

        assert "TokenDTO" in repr_str
        assert "access_token='test_token_123'" in repr_str

        # Pydantic's __str__ method shows field values, not the class name
        assert "access_token='test_token_123'" in str_str

    def test_outbound_token_field_access(self) -> None:
        """Test field access patterns for OutboundToken.

        Validates common usage patterns for accessing the access_token field.
        """
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token="bearer_token_xyz",
            iat=now,
            exp=now + timedelta(hours=1)
        )

        # Direct field access
        assert token.access_token == "bearer_token_xyz"
        assert token.iat == now
        assert token.exp == now + timedelta(hours=1)

        # Field access via getattr
        assert getattr(token, "access_token") == "bearer_token_xyz"

        # Check field exists
        assert hasattr(token, "access_token")
        assert hasattr(token, "iat")
        assert hasattr(token, "exp")

    def test_outbound_token_immutability(self) -> None:
        """Test that OutboundToken fields can be modified after creation.

        Validates the mutability behavior of the model.
        """
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token="original_token",
            iat=now,
            exp=now + timedelta(hours=1)
        )

        # Pydantic models are mutable by default
        token.access_token = "new_token"
        assert token.access_token == "new_token"

    def test_outbound_token_with_special_characters(self) -> None:
        """Test OutboundToken with special characters in token.

        Validates that special characters in access_token are handled correctly.
        """
        special_token = "token-with_special.chars!@#$%^&*()+=[]{}|;:,.<>?"
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token=special_token,
            iat=now,
            exp=now + timedelta(hours=1)
        )

        assert token.access_token == special_token

    def test_outbound_token_with_grant_type(self) -> None:
        """Test OutboundToken with grant_type specified.

        Validates that grant_type is properly set and serialized.
        """
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token="test_token",
            grant_type=GrantType.CLIENT_CREDENTIALS,
            iat=now,
            exp=now + timedelta(hours=1)
        )

        assert token.access_token == "test_token"
        assert token.grant_type == GrantType.CLIENT_CREDENTIALS
        assert token.token_type == "Bearer"

    def test_outbound_token_without_grant_type(self) -> None:
        """Test OutboundToken without grant_type (default None).

        Validates that grant_type defaults to None when not specified.
        """
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token="test_token",
            iat=now,
            exp=now + timedelta(hours=1)
        )

        assert token.access_token == "test_token"
        assert token.grant_type is None
        assert token.token_type == "Bearer"

    def test_outbound_token_all_grant_types(self) -> None:
        """Test OutboundToken with all available grant types.

        Validates that all grant types from the enum are accepted.
        """
        now = datetime.now(timezone.utc)
        for grant_type in GrantType:
            token = TokenDTO(
                access_token="test_token",
                grant_type=grant_type,
                iat=now,
                exp=now + timedelta(hours=1)
            )
            assert token.grant_type == grant_type

    def test_outbound_token_custom_token_type(self) -> None:
        """Test OutboundToken with custom token_type.

        Validates that token_type can be customized from default Bearer.
        """
        now = datetime.now(timezone.utc)
        token = TokenDTO(
            access_token="test_token",
            token_type="MAC",
            iat=now,
            exp=now + timedelta(hours=1)
        )

        assert token.access_token == "test_token"
        assert token.token_type == "MAC"

    def test_outbound_token_full_oauth_response(self) -> None:
        """Test OutboundToken with all OAuth fields populated.

        Validates a complete OAuth token response structure.
        """
        now = datetime.now(timezone.utc)
        exp_time = now + timedelta(hours=1)
        token = TokenDTO(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            grant_type=GrantType.AUTHORIZATION_CODE,
            token_type="Bearer",
            iat=now,
            exp=exp_time
        )

        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        assert token.grant_type == GrantType.AUTHORIZATION_CODE
        assert token.token_type == "Bearer"
        assert token.iat == now
        assert token.exp == exp_time

    def test_outbound_token_model_dump_with_oauth_fields(self) -> None:
        """Test model serialization with OAuth fields.

        Validates that OAuth fields are properly included in serialization.
        """
        now = datetime.now(timezone.utc)
        exp_time = now + timedelta(hours=1)
        token = TokenDTO(
            access_token="test_token_123",
            grant_type=GrantType.CLIENT_CREDENTIALS,
            token_type="Bearer",
            iat=now,
            exp=exp_time
        )
        data = token.model_dump()

        expected = {
            "access_token": "test_token_123",
            "grant_type": "client_credentials",
            "token_type": "Bearer",
            "iat": now,
            "exp": exp_time
        }
        assert data == expected
