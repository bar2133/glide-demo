"""Unit tests for longest prefix match functionality in TDProvider."""

import pytest
from unittest.mock import Mock
from common_components.services.telco_directory.providers.abs_provider import TDProvider
from common_components.services.telco_directory.models.td_data import TDData, SingleTelcoData


class ConcreteTDProvider(TDProvider):
    """Concrete implementation of TDProvider for testing purposes."""

    provider_type = Mock()
    config_type = Mock

    async def load(self):
        """Mock implementation of load method."""
        pass


class TestLongestPrefixMatch:
    """Test class for longest prefix match functionality."""

    @pytest.fixture
    def provider(self) -> ConcreteTDProvider:
        """Create a concrete TDProvider instance for testing.

        Returns:
            ConcreteTDProvider instance with test data loaded.
        """
        provider = ConcreteTDProvider()
        provider.loaded = True

        # Setup test data similar to the YAML structure
        test_data = TDData(prefixes={
            "97205": SingleTelcoData(
                base_url="http://telco-orange:8080",
                client_id="ORANGE_DEMO_ID",
                client_secret="ORANGE_DEMO_SECRET"
            ),
            "972050": SingleTelcoData(
                base_url="http://telco-vodafone:8081",
                client_id="VF_DEMO_ID",
                client_secret="VF_DEMO_SECRET"
            ),
            "4477": SingleTelcoData(
                base_url="http://telco-vodafone:8081",
                client_id="VF_UK_ID",
                client_secret="VF_UK_SECRET"
            ),
            "123": SingleTelcoData(
                base_url="http://test:8082",
                client_id="TEST_ID",
                client_secret="TEST_SECRET"
            )
        })

        provider.data = test_data
        return provider

    def test_find_longest_prefix_match_exact_match(self, provider: ConcreteTDProvider):
        """Test longest prefix match with exact match scenarios.

        Args:
            provider: The TDProvider instance with test data.
        """
        # Test exact matches - algorithm uses startswith and returns longest match first
        assert provider._find_longest_prefix_match("97205") == "97205"  # exact match
        assert provider._find_longest_prefix_match("972050") == "972050"  # exact match
        assert provider._find_longest_prefix_match("4477") == "4477"  # exact match
        assert provider._find_longest_prefix_match("123") == "123"  # exact match

    def test_find_longest_prefix_match_longer_query(self, provider: ConcreteTDProvider):
        """Test longest prefix match with longer query strings.

        Args:
            provider: The TDProvider instance with test data.
        """
        # Test longer queries - algorithm finds longest prefix that matches start
        assert provider._find_longest_prefix_match("97205123456") == "97205"  # 97205 matches start
        assert provider._find_longest_prefix_match("972050789") == "972050"  # 972050 matches start (longer)
        assert provider._find_longest_prefix_match("4477999") == "4477"  # 4477 matches start
        assert provider._find_longest_prefix_match("123456789") == "123"  # 123 matches start

    def test_find_longest_prefix_match_chooses_longest(self, provider: ConcreteTDProvider):
        """Test that longest prefix match chooses the longest matching prefix.

        Args:
            provider: The TDProvider instance with test data.
        """
        # Query that could match both "97205" and "972050" should return longest first
        assert provider._find_longest_prefix_match("972050123") == "972050"  # 972050 is longer and matches
        assert provider._find_longest_prefix_match("9720512345") == "97205"  # only 97205 matches start

    def test_find_longest_prefix_match_no_match(self, provider: ConcreteTDProvider):
        """Test longest prefix match with no matching prefixes.

        Args:
            provider: The TDProvider instance with test data.
        """
        # Test queries that don't start with any prefix
        assert provider._find_longest_prefix_match("999") is None  # doesn't start with any prefix
        assert provider._find_longest_prefix_match("555123") is None  # doesn't start with any prefix
        assert provider._find_longest_prefix_match("") is None  # empty query

    def test_find_longest_prefix_match_no_data(self):
        """Test longest prefix match when data is None or empty."""
        provider = ConcreteTDProvider()
        provider.loaded = True
        provider.data = None

        assert provider._find_longest_prefix_match("97205") is None

        # Test with empty prefixes
        provider.data = TDData(prefixes={})
        assert provider._find_longest_prefix_match("97205") is None

    @pytest.mark.asyncio
    async def test_get_telco_data_exact_match_priority(self, provider: ConcreteTDProvider):
        """Test that exact matches are prioritized over prefix matches.

        Args:
            provider: The TDProvider instance with test data.
        """
        # Exact match should be returned directly
        result = await provider.get_telco_data("972", "05")
        assert result is not None
        assert result.client_id == "ORANGE_DEMO_ID"

    @pytest.mark.asyncio
    async def test_get_telco_data_prefix_match(self, provider: ConcreteTDProvider):
        """Test get_telco_data with prefix matching.

        Args:
            provider: The TDProvider instance with test data.
        """
        # Should match "97205" prefix
        result = await provider.get_telco_data("972", "05123456")
        assert result is not None
        assert result.client_id == "ORANGE_DEMO_ID"  # 97205 prefix

        # Should match "972050" prefix (longer match)
        result = await provider.get_telco_data("972", "050789")
        assert result is not None
        assert result.client_id == "VF_DEMO_ID"

    @pytest.mark.asyncio
    async def test_get_telco_data_no_match(self, provider: ConcreteTDProvider):
        """Test get_telco_data with no matching prefix.

        Args:
            provider: The TDProvider instance with test data.
        """
        # "999123" doesn't start with any prefix
        result = await provider.get_telco_data("999", "123")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_telco_data_not_loaded(self):
        """Test get_telco_data when provider is not loaded."""
        provider = ConcreteTDProvider()
        provider.loaded = False

        with pytest.raises(RuntimeError, match="Telco directory not loaded"):
            await provider.get_telco_data("972", "05")
