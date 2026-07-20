from pydantic import BaseModel, Field, ConfigDict

class ReviewCreateModel(BaseModel):
    rating: float
    comment: str

class ReviewUpdateModel(BaseModel):
    rating: int | None = None
    comment: str | None = None

class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str

class ReviewResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserSummary
    rating: float
    comment: str