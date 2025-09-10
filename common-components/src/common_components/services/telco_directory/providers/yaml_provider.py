from common_components.services.telco_directory.providers.abs_provider import TDProvider
from common_components.services.telco_directory.configs.yaml_provider_config import TDYamlConfig
from common_components.services.telco_directory.enums.providers import TDProvidersTypes
import yaml
from common_components.services.telco_directory.models.td_data import TDData
from typing import cast


class TDYamlProvider(TDProvider):
    """YAML-based implementation of telco directory data provider.

    This provider loads telco directory data from a YAML file specified in the configuration.
    It inherits from TDProvider and implements the abstract load method to read and parse
    YAML files containing telco data with prefixes mapped to telco configurations.

    The provider reads the YAML file path from TDYamlConfig and parses the content into
    a TDData model containing prefixes and their associated SingleTelcoData entries.
    Error handling is implemented for both file I/O operations and YAML parsing.
    """
    provider_type = TDProvidersTypes.YAML
    config_type = TDYamlConfig

    async def load(self) -> None:
        """Load telco directory data from the configured YAML file.

        This method implements the abstract load method from TDProvider. It reads the YAML file
        specified in the configuration path, parses its content using yaml.safe_load, and
        converts it into a TDData model. The method includes error handling for both file
        I/O operations and YAML parsing, logging errors before re-raising exceptions.

        The method sets self.loaded to True only after successful loading and parsing of the data.
        If the provider is already loaded, the method returns early without reloading.

        Raises:
            Exception: If there's an error loading the YAML file or parsing its content.
        """
        if self.loaded:
            return
        try:
            with open(cast(TDYamlConfig, self.config).path, "r") as file:
                yaml_content = yaml.safe_load(file)
        except Exception as e:
            self.logger.error(f"Error loading YAML file: {e}")
            raise e
        try:
            self.data = TDData(**yaml_content)
        except Exception as e:
            self.logger.error(f"Error parsing YAML file: {e}")
            raise e
        self.loaded = True
