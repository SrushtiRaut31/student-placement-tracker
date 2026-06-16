# Student Placement Tracker - Pydantic Schemas
# Request/Response validation models for FastAPI endpoints

from pydantic import BaseModel, Field, validator
from typing import Optional, List


class UserRegister(BaseModel):
    """Request schema for user registration."""
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the student")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    confirm_password: str = Field(..., description="Password confirmation")

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserLogin(BaseModel):
    """Request schema for user login."""
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: int
    name: str


class TokenResponse(BaseModel):
    """Response schema for successful login."""
    message: str
    token: str
    user: UserResponse


class SkillCreate(BaseModel):
    """Request schema for creating a skill."""
    skill_name: str = Field(..., min_length=1, max_length=200, description="Name of the skill (e.g., Python, Java)")


class SkillResponse(BaseModel):
    """Response schema for a skill."""
    id: int
    student_id: int
    skill_name: str
    created_at: Optional[str] = None


class ApplicationCreate(BaseModel):
    """Request schema for creating a placement application."""
    company_name: str = Field(..., min_length=1, max_length=200, description="Name of the company applied to")
    status: str = Field(default="Applied", description="Application status (Applied, Interview Scheduled, Selected, Rejected)")


class ApplicationResponse(BaseModel):
    """Response schema for an application."""
    id: int
    student_id: int
    company_name: str
    status: str
    date_applied: Optional[str] = None
    created_at: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str