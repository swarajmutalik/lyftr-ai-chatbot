from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ChatRequest(BaseModel):
    session_id: str = Field(
        min_length=1,
        max_length=128
    )
    
    message: str = Field(
        min_length=1,
        max_length=4000
    )
    
    system_prompt: Optional[str] = None
    
    
    @field_validator("message", "session_id")
    @classmethod
    def validate_text(cls, value: str, info) -> str:
        value = value.strip()

        max_length = (
            4000 if info.field_name == "message"
            else 128
        )

        if not 1 <= len(value) <= max_length:
            raise ValueError(
                f"Must contain 1 to {max_length} characters"
            )

        return value
