"""FastAPI application providing problem generation endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from tcg.core.generator import ProblemGenerator
from tcg.models.problem import Difficulty
from tcg.services.output_writer import OutputWriter
from tcg.utils.security import JWTManager, UserClaims
from tcg.utils.settings import Settings, load_settings

settings: Settings = load_settings()
jwt_manager = JWTManager(settings)

bearer_scheme = HTTPBearer(auto_error=False)
app = FastAPI(title=settings.app.project_name, version="0.1.0")

generator = ProblemGenerator(output_writer=OutputWriter(settings.output_dir))

_FAKE_USERS: Dict[str, Dict[str, List[str]]] = {
    "admin@example.com": {"password": "admin", "roles": ["admin", "reviewer"]},
    "setter@example.com": {"password": "setter", "roles": ["setter"]},
}


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PlaceholderProblemRequest(BaseModel):
    problem_code: str = Field(..., pattern=r"^[A-Z0-9_-]{3,32}$")
    title: str
    difficulty: Difficulty = Difficulty.MEDIUM
    topic: str
    tags: List[str] = Field(default_factory=list)
    seed: Optional[int] = None
    num_examples: int = Field(default=1, ge=1, le=10)


class PlaceholderProblemResponse(BaseModel):
    output_path: Path


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/token", response_model=TokenResponse)
def login(data: TokenRequest) -> TokenResponse:
    record = _FAKE_USERS.get(data.username)
    if not record or record["password"] != data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = jwt_manager.create_access_token(subject=data.username, roles=record["roles"])
    return TokenResponse(access_token=token)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserClaims:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        return jwt_manager.decode(credentials.credentials)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


@app.post("/problems/placeholder", response_model=PlaceholderProblemResponse)
def create_placeholder(
    request: PlaceholderProblemRequest,
    user: UserClaims = Depends(get_current_user),
) -> PlaceholderProblemResponse:
    if "setter" not in user.roles and "admin" not in user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    output_dir = generator.generate_placeholder(
        title=request.title,
        problem_code=request.problem_code,
        difficulty=request.difficulty,
        topic=request.topic,
        tags=request.tags,
        seed=request.seed,
        num_examples=request.num_examples,
    )

    return PlaceholderProblemResponse(output_path=output_dir)
