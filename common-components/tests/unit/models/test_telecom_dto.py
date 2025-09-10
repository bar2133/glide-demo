"""Functional tests for TelecomDTO model."""

import pytest
from pydantic import ValidationError
from common_components.models.telecom_dto import TelecomIdentifierDTO


class TestTelecomDTO:
    """Test class for TelecomDTO model functionality."""

    def test_valid_telecom_dto_creation(self) -> None:
        """Test creating a valid TelecomDTO instance.

        Validates that a TelecomDTO can be created with valid MCC and SN values.
        """
        # Test with valid data
        dto = TelecomIdentifierDTO(mcc="123", sn="6789012")

        assert dto.mcc == "123"
        assert dto.sn == "6789012"

    def test_telecom_dto_with_minimum_values(self) -> None:
        """Test creating TelecomDTO with minimum valid values.

        Validates that TelecomDTO works with the smallest possible valid inputs.
        """
        dto = TelecomIdentifierDTO(mcc="1", sn="1")

        assert dto.mcc == "1"
        assert dto.sn == "1"

    def test_telecom_dto_coerce_numbers_to_str(self) -> None:
        """Test that numbers are coerced to strings.

        Validates the ConfigDict setting coerce_numbers_to_str=True works correctly.
        """
        dto = TelecomIdentifierDTO(mcc="123", sn="6789012")

        assert dto.mcc == "123"
        assert dto.sn == "6789012"
        assert isinstance(dto.mcc, str)
        assert isinstance(dto.sn, str)

    def test_mcc_validation_empty_string(self) -> None:
        """Test MCC validation with empty string.

        Validates that empty MCC raises ValidationError.
        """
        with pytest.raises(ValidationError) as exc_info:
            TelecomIdentifierDTO(mcc="", sn="6789012")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("mcc",)
        assert "MCC must be between 1 to 3 digits" in errors[0]["msg"]

    def test_mcc_validation_too_long(self) -> None:
        """Test MCC validation with string longer than 3 characters.

        Validates that MCC longer than 3 digits raises ValidationError.
        """
        with pytest.raises(ValidationError) as exc_info:
            TelecomIdentifierDTO(mcc="1234", sn="6789012")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("mcc",)
        assert "MCC must be between 1 to 3 digits" in errors[0]["msg"]

    def test_mcc_validation_valid_lengths(self) -> None:
        """Test MCC validation with all valid lengths (1-3 digits).

        Validates that MCC with 1, 2, or 3 digits is accepted.
        """
        # Test 1 digit
        dto1 = TelecomIdentifierDTO(mcc="1", sn="6789012")
        assert dto1.mcc == "1"

        # Test 2 digits
        dto2 = TelecomIdentifierDTO(mcc="12", sn="6789012")
        assert dto2.mcc == "12"

        # Test 3 digits
        dto3 = TelecomIdentifierDTO(mcc="123", sn="6789012")
        assert dto3.mcc == "123"

    def test_mcc_validation_non_numeric(self) -> None:
        """Test MCC validation with non-numeric characters.

        Validates that MCC with non-numeric characters is still accepted as string.
        """
        # MCC can contain non-numeric characters as it's just a string field
        dto = TelecomIdentifierDTO(mcc="ABC", sn="6789012")
        assert dto.mcc == "ABC"
        assert dto.sn == "6789012"

    def test_sn_validation_empty_string(self) -> None:
        """Test SN validation with empty string.

        Validates that empty SN raises ValidationError.
        """
        with pytest.raises(ValidationError) as exc_info:
            TelecomIdentifierDTO(mcc="123", sn="")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("sn",)
        assert "SN cannot be empty" in errors[0]["msg"]

    def test_total_length_validation_valid(self) -> None:
        """Test total length validation with valid total length.

        Validates that combined length of MCC, MNC, and SN <= 15 is accepted.
        """
        # Total length = 3 + 12 = 15 (exactly at limit)
        dto = TelecomIdentifierDTO(mcc="123", sn="678901234567")

        assert dto.mcc == "123"
        assert dto.sn == "678901234567"

    def test_total_length_validation_invalid(self) -> None:
        """Test total length validation with invalid total length.

        Validates that combined length of MCC, MNC, and SN > 15 raises ValidationError.
        """
        with pytest.raises(ValidationError) as exc_info:
            # Total length = 3 + 13 = 16 (exceeds limit)
            TelecomIdentifierDTO(mcc="123", sn="7890123456789")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Total length must be less than 15" in errors[0]["msg"]

    def test_total_length_validation_edge_cases(self) -> None:
        """Test total length validation edge cases.

        Validates behavior at the boundary of the 15-character limit.
        """
        # Test exactly 15 characters (should pass)
        dto_valid = TelecomIdentifierDTO(mcc="123", sn="678901234567")
        assert len(dto_valid.mcc + dto_valid.sn) == 15

        # Test 16 characters (should fail)
        with pytest.raises(ValidationError):
            TelecomIdentifierDTO(mcc="123", sn="7890123456789")

    def test_model_dump(self) -> None:
        """Test model serialization to dictionary.

        Validates that the model can be properly serialized to a dictionary.
        """
        dto = TelecomIdentifierDTO(mcc="123", sn="6789012")
        data = dto.model_dump()

        expected = {"mcc": "123", "sn": "6789012"}
        assert data == expected

    def test_model_dump_json(self) -> None:
        """Test model serialization to JSON.

        Validates that the model can be properly serialized to JSON string.
        """
        dto = TelecomIdentifierDTO(mcc="123", sn="6789012")
        json_str = dto.model_dump_json()

        assert '"mcc":"123"' in json_str
        assert '"sn":"6789012"' in json_str

    def test_from_dict(self) -> None:
        """Test model creation from dictionary.

        Validates that TelecomDTO can be created from a dictionary.
        """
        data = {"mcc": "123", "sn": "6789012"}
        dto = TelecomIdentifierDTO(**data)

        assert dto.mcc == "123"
        assert dto.sn == "6789012"

    def test_multiple_validation_errors(self) -> None:
        """Test handling of multiple validation errors.

        Validates that multiple field validations can fail together.
        """
        with pytest.raises(ValidationError) as exc_info:
            TelecomIdentifierDTO(mcc="", sn="")

        errors = exc_info.value.errors()
        # Should have validation errors for both fields
        assert len(errors) == 2

        error_locs = [error["loc"] for error in errors]
        assert ("mcc",) in error_locs
        assert ("sn",) in error_locs

        # Check specific error messages
        mcc_error = next((e for e in errors if e["loc"] == ("mcc",)), None)
        sn_error = next((e for e in errors if e["loc"] == ("sn",)), None)

        assert mcc_error is not None
        assert sn_error is not None

        assert "MCC must be between 1 to 3 digits" in mcc_error["msg"]
        assert "SN cannot be empty" in sn_error["msg"]

    def test_equality(self) -> None:
        """Test equality comparison between TelecomDTO instances.

        Validates that two TelecomDTO instances with same values are equal.
        """
        dto1 = TelecomIdentifierDTO(mcc="123", sn="6789012")
        dto2 = TelecomIdentifierDTO(mcc="123", sn="6789012")
        dto3 = TelecomIdentifierDTO(mcc="124", sn="6789012")

        assert dto1 == dto2
        assert dto1 != dto3

    def test_repr_and_str(self) -> None:
        """Test string representation of TelecomDTO.

        Validates that the model has proper string representation.
        """
        dto = TelecomIdentifierDTO(mcc="123", sn="6789012")

        repr_str = repr(dto)
        str_str = str(dto)

        assert "TelecomIdentifierDTO" in repr_str
        assert "mcc='123'" in repr_str
        assert "sn='6789012'" in repr_str
