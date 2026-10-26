"""Validated API request and response models."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=256)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class FileInput(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=2_000_000)


class ScanCreate(BaseModel):
    project_name: str = Field(min_length=1, max_length=120)
    source: str = Field(default="web-upload", max_length=80)
    files: list[FileInput] = Field(min_length=1, max_length=500)


class FindingOut(BaseModel):
    rule_id: str
    title: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    category: str
    file_path: str
    line: int | None = None
    message: str
    recommendation: str


class ScanOut(BaseModel):
    id: int
    project_name: str
    source: str
    status: str
    risk_score: int
    files_scanned: int
    findings_count: int
    created_at: datetime
    findings: list[FindingOut] = []


class PolicyOut(BaseModel):
    id: str
    name: str
    description: str
    severity: str
    enabled: bool
