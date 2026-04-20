from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    clerk_user_id: str
    email: str | None
    full_name: str | None
    created_at: datetime

