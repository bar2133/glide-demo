from enum import StrEnum, auto


class TDProvidersTypes(StrEnum):
    """Enum for the different providers of the Telco Directory service.

    This enum defines the different providers that can be used to retrieve
    telco directory information.
    """
    YAML = auto()
