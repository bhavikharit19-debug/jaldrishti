"""
JalDrishti AI — Security, Role-Based Access Control & Audit Framework
Supports JWT Bearer token authentication, bcrypt password hashing,
jurisdictional authorization (State/District/Watershed), and statutory audit logging.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
import datetime
import bcrypt
import jwt
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.domain import AuditLog, User, Watershed, District

http_bearer = HTTPBearer(auto_error=False)

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    STATE_OFFICER = "STATE_OFFICER"
    DISTRICT_OFFICER = "DISTRICT_OFFICER"
    FIELD_OFFICER = "FIELD_OFFICER"
    ANALYST = "ANALYST"

def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt with a secure salt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Generate a signed PyJWT token with expiration claim."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (
        expires_delta or datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decode and validate a signed JWT token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

class RequestUser:
    """Represents the context of the calling user during request processing."""
    def __init__(
        self,
        user_id: str,
        role: UserRole,
        email: str = "",
        name: str = "",
        state_id: Optional[int] = None,
        district_id: Optional[int] = None,
        watershed_id: Optional[int] = None,
        is_authenticated: bool = False
    ):
        self.user_id = user_id
        self.role = role
        self.email = email
        self.name = name
        self.state_id = state_id
        self.district_id = district_id
        self.watershed_id = watershed_id
        self.is_authenticated = is_authenticated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "email": self.email,
            "name": self.name,
            "state_id": self.state_id,
            "district_id": self.district_id,
            "watershed_id": self.watershed_id,
            "is_authenticated": self.is_authenticated
        }

def get_current_user(
    auth_creds: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    x_user_id: Optional[str] = Header(None, description="Developer fallback User ID"),
    x_user_role: Optional[str] = Header(None, description="Developer fallback Role"),
    x_state_id: Optional[int] = Header(None, description="Developer fallback State ID"),
    x_district_id: Optional[int] = Header(None, description="Developer fallback District ID"),
    db: Session = Depends(get_db)
) -> RequestUser:
    """
    Resolves the calling officer's identity and jurisdictional scope.
    1. If a Bearer token is passed, strictly decodes and validates against the database.
    2. If developer headers are passed, constructs a RequestUser accordingly.
    3. If unauthenticated, gracefully defaults to an unauthenticated ANALYST context
       to maintain backward compatibility for existing read/demo endpoints.
    """
    if auth_creds and auth_creds.credentials:
        token = auth_creds.credentials
        try:
            payload = decode_access_token(token)
            email: str = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token payload",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        db_user = db.query(User).filter(User.email == email).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authenticated user no longer exists",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account has been deactivated by administrator",
                headers={"WWW-Authenticate": "Bearer"}
            )

        try:
            role = UserRole(db_user.role)
        except ValueError:
            role = UserRole.ANALYST

        return RequestUser(
            user_id=str(db_user.id),
            role=role,
            email=db_user.email,
            name=db_user.name,
            state_id=db_user.state_id,
            district_id=db_user.district_id,
            watershed_id=db_user.watershed_id,
            is_authenticated=True
        )

    # Developer header fallback for existing tests / dev harness
    if x_user_role or x_user_id:
        role_str = (x_user_role or "ANALYST").upper()
        try:
            role = UserRole(role_str)
        except ValueError:
            role = UserRole.ANALYST
        return RequestUser(
            user_id=x_user_id or "officer_demo",
            role=role,
            email=f"{x_user_id or 'officer_demo'}@jaldrishti.gov.in",
            name=x_user_id or "Demo Officer",
            state_id=x_state_id,
            district_id=x_district_id,
            is_authenticated=True
        )

    # Unauthenticated default (backward compatibility for public/demo endpoints)
    return RequestUser(
        user_id="anonymous",
        role=UserRole.ANALYST,
        email="guest@jaldrishti.gov.in",
        name="Guest Viewer",
        state_id=None,
        district_id=None,
        is_authenticated=False
    )

def require_authenticated_user(
    current_user: RequestUser = Depends(get_current_user)
) -> RequestUser:
    """Ensures the request originated from an authenticated officer."""
    if not current_user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in with official credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user

def require_roles(*allowed_roles: UserRole):
    """
    Factory creating a dependency that verifies the caller possesses one of the allowed roles.
    Raises 401 if unauthenticated, 403 if unauthorized.
    """
    def role_verifier(current_user: RequestUser = Depends(get_current_user)) -> RequestUser:
        if not current_user.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to perform this action.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: Insufficient permissions for role '{current_user.role.value}'."
            )
        return current_user
    return role_verifier

def check_jurisdiction(
    user: RequestUser,
    db: Session,
    watershed_id: Optional[int] = None,
    district_id: Optional[int] = None,
    state_id: Optional[int] = None
) -> None:
    """
    Enforces geographic access boundaries based on the officer's administrative role.
    - ADMIN: Unrestricted national jurisdiction.
    - ANALYST: Unrestricted read jurisdiction for analytical workflows.
    - STATE_OFFICER: Confined to their assigned state.
    - DISTRICT_OFFICER: Confined to their assigned district.
    - FIELD_OFFICER: Confined to their assigned micro-watershed or district.
    """
    if user.role in (UserRole.ADMIN, UserRole.ANALYST):
        return

    # Check State Officer Scope
    if user.role == UserRole.STATE_OFFICER:
        if state_id is not None and user.state_id is not None and state_id != user.state_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Jurisdictional access denied: Confined to assigned State ID {user.state_id}."
            )
        if district_id is not None and user.state_id is not None:
            dist = db.query(District).filter(District.id == district_id).first()
            if dist and dist.state_id != user.state_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Jurisdictional access denied: District {dist.name} is outside assigned State."
                )
        if watershed_id is not None and user.state_id is not None:
            ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
            if ws and ws.state_id != user.state_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Jurisdictional access denied: Watershed {ws.code} is outside assigned State."
                )

    # Check District Officer Scope
    elif user.role == UserRole.DISTRICT_OFFICER:
        if district_id is not None and user.district_id is not None and district_id != user.district_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Jurisdictional access denied: Confined to assigned District ID {user.district_id}."
            )
        if watershed_id is not None and user.district_id is not None:
            ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
            if ws and ws.district_id != user.district_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Jurisdictional access denied: Watershed {ws.code} is outside assigned District."
                )

    # Check Field Officer Scope
    elif user.role == UserRole.FIELD_OFFICER:
        if user.watershed_id is not None and watershed_id is not None and user.watershed_id != watershed_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Jurisdictional access denied: Field Officer confined to assigned Watershed ID {user.watershed_id}."
            )
        if district_id is not None and user.district_id is not None and user.district_id != district_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Jurisdictional access denied: Confined to assigned District ID {user.district_id}."
            )

def log_audit_event(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: str = "system",
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> Optional[AuditLog]:
    """
    Records an immutable audit event for government compliance, security monitoring, and change tracking.
    """
    try:
        log_entry = AuditLog(
            user_id=str(user_id),
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            details=details or {},
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception:
        db.rollback()
        return None
