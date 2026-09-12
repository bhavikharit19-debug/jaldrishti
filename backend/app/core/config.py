import os
import json
from typing import List, Union, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "JalDrishti"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    PORT: int = 8000
    
    DATABASE_URL: str = "sqlite:///./jaldrishti.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v
    
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["*"]
            if v == "*":
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(i).strip() for i in v if str(i).strip()]
        return ["*"]
    
    STORAGE_TYPE: str = "local"
    UPLOAD_DIR: str = "./uploads"
    
    # Authentication & Security
    SECRET_KEY: str = "jaldrishti_secret_gov_auth_2026_sih_secure"
    JWT_SECRET: Optional[str] = None
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    JWT_EXPIRATION_MINUTES: Optional[int] = None

    @property
    def jwt_secret_key(self) -> str:
        secret = self.JWT_SECRET or os.getenv("JWT_SECRET")
        if secret and secret.strip():
            return secret.strip()

        is_production = str(self.ENVIRONMENT).lower() in ("production", "prod") or not self.DEBUG
        if is_production:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: JWT_SECRET must be explicitly configured in production environment. "
                "Refusing to start with missing or default secret."
            )

        # Local development / automated testing fallback only (never used in production)
        return "dev-insecure-jwt-secret-key-change-in-production-only"

    @property
    def jwt_algorithm(self) -> str:
        return (self.JWT_ALGORITHM or os.getenv("JWT_ALGORITHM") or self.ALGORITHM or "HS256").strip()

    @property
    def jwt_expiration_minutes(self) -> int:
        return int(self.JWT_EXPIRATION_MINUTES or self.ACCESS_TOKEN_EXPIRE_MINUTES or 1440)
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )

settings = Settings()
