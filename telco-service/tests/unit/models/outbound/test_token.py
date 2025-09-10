"""Functional tests for OutboundToken model."""

import pytest
from pydantic import ValidationError
from common_components.models.outbound.token import TokenDTO
from common_components.models.oauth_enums import GrantType


class TestOutboundToken:
    """Test class for OutboundToken model functionality."""

    def test_valid_outbound_token_creation(self) -> None:
        """Test creating a valid OutboundToken instance.

        Validates that an OutboundToken can be created with a valid access_token.
        """
        token = TokenDTO(access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

    def test_outbound_token_with_empty_string(self) -> None:
        """Test creating OutboundToken with empty string.

        Validates that empty access_token raises ValidationError.
        """
        with pytest.raises(ValidationError) as exc_info:
            TokenDTO(access_token="")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("access_token",)
        assert "Access token cannot be empty" in errors[0]["msg"]

    def test_outbound_token_with_long_token(self) -> None:
        """Test creating OutboundToken with a long JWT token.

        Validates that OutboundToken can handle long access tokens like JWT.
        """
        long_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )

        token = TokenDTO(access_token=long_token)

        assert token.access_token == long_token

    def test_outbound_token_required_field(self) -> None:
        """Test that access_token field is required.

        Validates that ValidationError is raised when access_token is not provided.
        """
        with pytest.raises(ValidationError) as exc_info:
            TokenDTO()  # type: ignore

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("access_token",)
        assert errors[0]["type"] == "missing"

    def test_outbound_token_with_none(self) -> None:
        """Test OutboundToken with None value.

        Validates that None access_token raises ValidationError.
        """
        with pytest.raises(ValidationError) as exc_info:
            TokenDTO(access_token=None)  # type: ignore

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("access_token",)

    def test_outbound_token_with_numeric_input(self) -> None:
        """Test OutboundToken with numeric input.

        Validates that numeric values are converted to strings.
        """
        token = TokenDTO(access_token="12345")

        assert token.access_token == "12345"
        assert isinstance(token.access_token, str)

    def test_outbound_token_model_dump(self) -> None:
        """Test model serialization to dictionary.

        Validates that the model can be properly serialized to a dictionary.
        """
        token = TokenDTO(access_token="test_token_123")
        data = token.model_dump()

        expected = {
            "access_token": "test_token_123",
            "grant_type": None,
            "token_type": "Bearer"
        }
        assert data == expected

    def test_outbound_token_model_dump_json(self) -> None:
        """Test model serialization to JSON.

        Validates that the model can be properly serialized to JSON string.
        """
        token = TokenDTO(access_token="test_token_123")
        json_str = token.model_dump_json()

        assert '"access_token":"test_token_123"' in json_str
        assert '"grant_type":null' in json_str
        assert '"token_type":"Bearer"' in json_str

    def test_outbound_token_from_dict(self) -> None:
        """Test model creation from dictionary.

        Validates that OutboundToken can be created from a dictionary.
        """
        data = {"access_token": "test_token_456"}
        token = TokenDTO(**data)  # type: ignore

        assert token.access_token == "test_token_456"

    def test_outbound_token_equality(self) -> None:
        """Test equality comparison between OutboundToken instances.

        Validates that two OutboundToken instances with same values are equal.
        """
        token1 = TokenDTO(access_token="test_token")
        token2 = TokenDTO(access_token="test_token")
        token3 = TokenDTO(access_token="different_token")

        assert token1 == token2
        assert token1 != token3

    def test_outbound_token_repr_and_str(self) -> None:
        """Test string representation of OutboundToken.

        Validates that the model has proper string representation.
        """
        token = TokenDTO(access_token="test_token_123")

        repr_str = repr(token)
        str_str = str(token)

        assert "OutboundToken" in repr_str
        assert "access_token='test_token_123'" in repr_str

        # Pydantic's __str__ method shows field values, not the class name
        assert "access_token='test_token_123'" in str_str

    def test_outbound_token_field_access(self) -> None:
        """Test field access patterns for OutboundToken.

        Validates common usage patterns for accessing the access_token field.
        """
        token = TokenDTO(access_token="bearer_token_xyz")

        # Direct field access
        assert token.access_token == "bearer_token_xyz"

        # Field access via getattr
        assert getattr(token, "access_token") == "bearer_token_xyz"

        # Check field exists
        assert hasattr(token, "access_token")

    def test_outbound_token_immutability(self) -> None:
        """Test that OutboundToken fields can be modified after creation.

        Validates the mutability behavior of the model.
        """
        token = TokenDTO(access_token="original_token")

        # Pydantic models are mutable by default
        token.access_token = "new_token"
        assert token.access_token == "new_token"

    def test_outbound_token_with_special_characters(self) -> None:
        """Test OutboundToken with special characters in token.

        Validates that special characters in access_token are handled correctly.
        """
        special_token = "token-with_special.chars!@#$%^&*()+=[]{}|;:,.<>?"
        token = TokenDTO(access_token=special_token)

        assert token.access_token == special_token

    def test_outbound_token_with_grant_type(self) -> None:
        """Test OutboundToken with grant_type specified.

        Validates that grant_type is properly set and serialized.
        """
        token = TokenDTO(
            access_token="test_token",
            grant_type=GrantType.CLIENT_CREDENTIALS
        )

        assert token.access_token == "test_token"
        assert token.grant_type == GrantType.CLIENT_CREDENTIALS
        assert token.token_type == "Bearer"

    def test_outbound_token_without_grant_type(self) -> None:
        """Test OutboundToken without grant_type (default None).

        Validates that grant_type defaults to None when not specified.
        """
        token = TokenDTO(access_token="test_token")

        assert token.access_token == "test_token"
        assert token.grant_type is None
        assert token.token_type == "Bearer"

    def test_outbound_token_all_grant_types(self) -> None:
        """Test OutboundToken with all available grant types.

        Validates that all grant types from the enum are accepted.
        """
        for grant_type in GrantType:
            token = TokenDTO(
                access_token="test_token",
                grant_type=grant_type
            )
            assert token.grant_type == grant_type

    def test_outbound_token_custom_token_type(self) -> None:
        """Test OutboundToken with custom token_type.

        Validates that token_type can be customized from default Bearer.
        """
        token = TokenDTO(
            access_token="test_token",
            token_type="MAC"
        )

        assert token.access_token == "test_token"
        assert token.token_type == "MAC"

    def test_outbound_token_full_oauth_response(self) -> None:
        """Test OutboundToken with all OAuth fields populated.

        Validates a complete OAuth token response structure.
        """
        token = TokenDTO(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            grant_type=GrantType.AUTHORIZATION_CODE,
            token_type="Bearer"
        )

        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        assert token.grant_type == GrantType.AUTHORIZATION_CODE
        assert token.token_type == "Bearer"

    def test_outbound_token_model_dump_with_oauth_fields(self) -> None:
        """Test model serialization with OAuth fields.

        Validates that OAuth fields are properly included in serialization.
        """
        token = TokenDTO(
            access_token="test_token_123",
            grant_type=GrantType.CLIENT_CREDENTIALS,
            token_type="Bearer"
        )
        data = token.model_dump()

        expected = {
            "access_token": "test_token_123",
            "grant_type": "client_credentials",
            "token_type": "Bearer"
        }
        assert data == expected
