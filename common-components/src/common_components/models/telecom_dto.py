from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class TelecomIdentifierDTO(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    mcc: str
    sn: str

    @field_validator("mcc")
    @staticmethod
    def validate_mcc(v: str) -> str:
        if not len(v) or len(v) > 3:
            raise ValueError("MCC must be between 1 to 3 digits")
        return v

    @field_validator("sn")
    @staticmethod
    def validate_sn(v: str) -> str:
        if not len(v):
            raise ValueError("SN cannot be empty")
        return v

    @model_validator(mode='before')
    @staticmethod
    def validate_length(fields: dict) -> dict:
        total_length = sum(len(value) for value in fields.values())
        if total_length > 15:
            raise ValueError("Total length must be less than 15")
        return fields
