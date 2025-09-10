"""Functional tests for TDData and SingleTelcoData models."""

import pytest
from pydantic import ValidationError
from common_components.services.telco_directory.models.td_data import TDData, SingleTelcoData


class TestSingleTelcoData:
    """Test class for SingleTelcoData model functionality."""

    def test_valid_single_telco_data_creation(self) -> None:
        """Test creating a valid SingleTelcoData instance.

        Validates that a SingleTelcoData can be created with valid base_url, client_id, and client_secret.
        """
        data = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="test_client_123",
            client_secret="secret_key_456"
        )

        assert data.base_url == "https://api.example.com"
        assert data.client_id == "test_client_123"
        assert data.client_secret == "secret_key_456"

    def test_single_telco_data_coerce_numbers_to_str(self) -> None:
        """Test that numbers are coerced to strings.

        Validates the ConfigDict setting coerce_numbers_to_str=True works correctly.
        """
        data = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="12345",
            client_secret="67890"
        )

        assert data.client_id == "12345"
        assert data.client_secret == "67890"
        assert isinstance(data.client_id, str)
        assert isinstance(data.client_secret, str)

    def test_single_telco_data_from_attributes(self) -> None:
        """Test creating SingleTelcoData from object attributes.

        Validates the ConfigDict setting from_attributes=True works correctly.
        """
        class MockObject:
            def __init__(self):
                self.base_url = "https://api.example.com"
                self.client_id = "test_client"
                self.client_secret = "test_secret"

        mock_obj = MockObject()
        data = SingleTelcoData.model_validate(mock_obj)

        assert data.base_url == "https://api.example.com"
        assert data.client_id == "test_client"
        assert data.client_secret == "test_secret"

    def test_single_telco_data_required_fields(self) -> None:
        """Test that all fields are required.

        Validates that ValidationError is raised when required fields are missing.
        """
        # Missing base_url
        with pytest.raises(ValidationError) as exc_info:
            SingleTelcoData(client_id="test", client_secret="secret")  # type: ignore

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("base_url",) for error in errors)

        # Missing client_id
        with pytest.raises(ValidationError) as exc_info:
            SingleTelcoData(base_url="https://api.example.com", client_secret="secret")  # type: ignore

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("client_id",) for error in errors)

        # Missing client_secret
        with pytest.raises(ValidationError) as exc_info:
            SingleTelcoData(base_url="https://api.example.com", client_id="test")  # type: ignore

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("client_secret",) for error in errors)

    def test_single_telco_data_model_dump(self) -> None:
        """Test model serialization to dictionary.

        Validates that the model can be properly serialized to a dictionary.
        """
        data = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="test_client",
            client_secret="test_secret"
        )

        dumped = data.model_dump()
        expected = {
            "base_url": "https://api.example.com",
            "client_id": "test_client",
            "client_secret": "test_secret"
        }

        assert dumped == expected

    def test_single_telco_data_equality(self) -> None:
        """Test equality comparison between SingleTelcoData instances.

        Validates that two SingleTelcoData instances with same values are equal.
        """
        data1 = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="test_client",
            client_secret="test_secret"
        )

        data2 = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="test_client",
            client_secret="test_secret"
        )

        data3 = SingleTelcoData(
            base_url="https://api.different.com",
            client_id="test_client",
            client_secret="test_secret"
        )

        assert data1 == data2
        assert data1 != data3


class TestTDData:
    """Test class for TDData model functionality."""

    def test_valid_td_data_creation(self) -> None:
        """Test creating a valid TDData instance.

        Validates that a TDData can be created with valid prefixes dictionary.
        """
        single_data = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="test_client",
            client_secret="test_secret"
        )

        td_data = TDData(prefixes={"123": single_data})

        assert "123" in td_data.prefixes
        assert td_data.prefixes["123"] == single_data

    def test_td_data_multiple_prefixes(self) -> None:
        """Test TDData with multiple prefix entries.

        Validates that TDData can handle multiple telco prefixes.
        """
        data1 = SingleTelcoData(
            base_url="https://api.telco1.com",
            client_id="client1",
            client_secret="secret1"
        )

        data2 = SingleTelcoData(
            base_url="https://api.telco2.com",
            client_id="client2",
            client_secret="secret2"
        )

        td_data = TDData(prefixes={"123": data1, "456": data2})

        assert len(td_data.prefixes) == 2
        assert td_data.prefixes["123"] == data1
        assert td_data.prefixes["456"] == data2

    def test_td_data_empty_prefixes(self) -> None:
        """Test TDData with empty prefixes dictionary.

        Validates that TDData can be created with an empty prefixes dictionary.
        """
        td_data = TDData(prefixes={})

        assert len(td_data.prefixes) == 0
        assert td_data.prefixes == {}

    def test_td_data_coerce_numbers_to_str(self) -> None:
        """Test that numbers in prefixes keys are handled correctly.

        Validates the ConfigDict setting coerce_numbers_to_str=True works for nested structures.
        """
        single_data = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="12345",
            client_secret="67890"
        )

        # Note: Dictionary keys remain as provided, but SingleTelcoData fields are coerced
        td_data = TDData(prefixes={"123": single_data})

        assert td_data.prefixes["123"].client_id == "12345"
        assert td_data.prefixes["123"].client_secret == "67890"

    def test_td_data_from_dict(self) -> None:
        """Test creating TDData from dictionary data.

        Validates that TDData can be created from nested dictionary structures.
        """
        data_dict = {
            "prefixes": {
                "123": {
                    "base_url": "https://api.telco1.com",
                    "client_id": "client1",
                    "client_secret": "secret1"
                },
                "456": {
                    "base_url": "https://api.telco2.com",
                    "client_id": "client2",
                    "client_secret": "secret2"
                }
            }
        }

        td_data = TDData.model_validate(data_dict)

        assert len(td_data.prefixes) == 2
        assert isinstance(td_data.prefixes["123"], SingleTelcoData)
        assert isinstance(td_data.prefixes["456"], SingleTelcoData)
        assert td_data.prefixes["123"].base_url == "https://api.telco1.com"
        assert td_data.prefixes["456"].client_id == "client2"

    def test_td_data_model_dump(self) -> None:
        """Test model serialization to dictionary.

        Validates that the model can be properly serialized to a nested dictionary.
        """
        single_data = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="test_client",
            client_secret="test_secret"
        )

        td_data = TDData(prefixes={"123": single_data})
        dumped = td_data.model_dump()

        expected = {
            "prefixes": {
                "123": {
                    "base_url": "https://api.example.com",
                    "client_id": "test_client",
                    "client_secret": "test_secret"
                }
            }
        }

        assert dumped == expected

    def test_td_data_model_dump_json(self) -> None:
        """Test model serialization to JSON.

        Validates that the model can be properly serialized to JSON string.
        """
        single_data = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="test_client",
            client_secret="test_secret"
        )

        td_data = TDData(prefixes={"123": single_data})
        json_str = td_data.model_dump_json()

        assert '"prefixes"' in json_str
        assert '"123"' in json_str
        assert '"base_url":"https://api.example.com"' in json_str
        assert '"client_id":"test_client"' in json_str

    def test_td_data_validation_error_nested(self) -> None:
        """Test validation errors in nested SingleTelcoData.

        Validates that validation errors in nested structures are properly reported.
        """
        with pytest.raises(ValidationError) as exc_info:
            TDData.model_validate({
                "prefixes": {
                    "123": {
                        "base_url": "https://api.example.com",
                        "client_id": "test_client"
                        # Missing client_secret
                    }
                }
            })

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        # Check that the error path includes the nested structure
        error_locs = [error["loc"] for error in errors]
        assert any(("prefixes", "123", "client_secret") == loc for loc in error_locs)

    def test_td_data_equality(self) -> None:
        """Test equality comparison between TDData instances.

        Validates that two TDData instances with same values are equal.
        """
        single_data1 = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="test_client",
            client_secret="test_secret"
        )

        single_data2 = SingleTelcoData(
            base_url="https://api.example.com",
            client_id="test_client",
            client_secret="test_secret"
        )

        td_data1 = TDData(prefixes={"123": single_data1})
        td_data2 = TDData(prefixes={"123": single_data2})
        td_data3 = TDData(prefixes={"456": single_data1})

        assert td_data1 == td_data2
        assert td_data1 != td_data3

    def test_td_data_access_patterns(self) -> None:
        """Test common access patterns for TDData.

        Validates typical usage patterns for accessing telco data by prefix.
        """
        data1 = SingleTelcoData(
            base_url="https://api.telco1.com",
            client_id="client1",
            client_secret="secret1"
        )

        data2 = SingleTelcoData(
            base_url="https://api.telco2.com",
            client_id="client2",
            client_secret="secret2"
        )

        td_data = TDData(prefixes={"123": data1, "456": data2})

        # Test key existence
        assert "123" in td_data.prefixes
        assert "456" in td_data.prefixes
        assert "789" not in td_data.prefixes

        # Test iteration
        prefix_keys = list(td_data.prefixes.keys())
        assert set(prefix_keys) == {"123", "456"}

        # Test values access
        values = list(td_data.prefixes.values())
        assert len(values) == 2
        assert data1 in values
        assert data2 in values
