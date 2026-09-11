"""
JalDrishti AI — Administrative User Management, Access Request & Audit Endpoints
Enforces strict ADMIN role authorization on all operations.
"""

from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.security import (
    require_roles, hash_password, log_audit_event,
    RequestUser, UserRole
)
from app.models.domain import User, AccessRequest, AuditLog
from app.schemas.schemas import (
    UserResponse, UserCreate, UserUpdate,
    AccessRequestResponse, AccessRequestReview, AuditLogResponse
)

router = APIRouter()

# ==========================================
# User Management (Admin Only)
# ==========================================

@router.get("/users", response_model=List[UserResponse], summary="List registered users")
def list_users(
    role: Optional[str] = Query(None, description="Filter by assigned role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_admin: RequestUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Lists registered departmental officers and administrators with optional role/active filters."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role.upper())
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(u) for u in users]

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new officer account")
def create_user(
    user_in: UserCreate,
    request: Request,
    current_admin: RequestUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Directly provisions an officer account with assigned role and jurisdiction."""
    client_ip = request.client.host if request.client else "unknown"

    existing = db.query(User).filter(User.email == user_in.email.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    valid_roles = [r.value for r in UserRole]
    if user_in.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{user_in.role}'. Allowed: {valid_roles}"
        )

    new_user = User(
        name=user_in.name.strip(),
        email=user_in.email.strip(),
        password_hash=hash_password(user_in.password),
        role=user_in.role,
        state_id=user_in.state_id,
        district_id=user_in.district_id,
        watershed_id=user_in.watershed_id,
        organization=user_in.organization,
        designation=user_in.designation,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit_event(
        db, action="USER_CREATED", resource_type="USER",
        resource_id=str(new_user.id), user_id=current_admin.user_id,
        details={"created_email": new_user.email, "role": new_user.role},
        ip_address=client_ip
    )

    return UserResponse.model_validate(new_user)

@router.patch("/users/{user_id}", response_model=UserResponse, summary="Update user account")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request,
    current_admin: RequestUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Updates an officer's role, jurisdictional assignment, active status, or password."""
    client_ip = request.client.host if request.client else "unknown"

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_dict = user_update.model_dump(exclude_unset=True)
    if "password" in update_dict and update_dict["password"]:
        user.password_hash = hash_password(update_dict.pop("password"))

    if "role" in update_dict:
        valid_roles = [r.value for r in UserRole]
        if update_dict["role"] not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Allowed: {valid_roles}"
            )

    for field, val in update_dict.items():
        setattr(user, field, val)

    user.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(user)

    log_audit_event(
        db, action="USER_UPDATED", resource_type="USER",
        resource_id=str(user.id), user_id=current_admin.user_id,
        details={"updated_fields": list(update_dict.keys())},
        ip_address=client_ip
    )

    return UserResponse.model_validate(user)

# ==========================================
# Access Request Review & Provisioning (Admin Only)
# ==========================================

@router.get("/access-requests", response_model=List[AccessRequestResponse], summary="List access requests")
def list_access_requests(
    status_filter: Optional[str] = Query(None, description="Filter by status: PENDING, APPROVED, REJECTED"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_admin: RequestUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Lists submitted public access requests with optional status filtering."""
    query = db.query(AccessRequest)
    if status_filter:
        query = query.filter(AccessRequest.status == status_filter.upper())
    
    requests = query.order_by(desc(AccessRequest.created_at)).offset(skip).limit(limit).all()
    return [AccessRequestResponse.model_validate(r) for r in requests]

@router.post("/access-requests/{request_id}/approve", response_model=UserResponse, summary="Approve access request")
def approve_access_request(
    request_id: int,
    review: AccessRequestReview,
    request: Request,
    current_admin: RequestUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Approves an official access request and provisions an active officer account.
    Assigns temporary password or default demo password.
    """
    client_ip = request.client.host if request.client else "unknown"

    req = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access request not found")

    if req.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve request with status '{req.status}'. Only PENDING requests can be approved."
        )

    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        existing_user.is_active = True
        req.status = "APPROVED"
        req.reviewed_by = int(current_admin.user_id) if current_admin.user_id.isdigit() else None
        req.reviewed_at = datetime.datetime.utcnow()
        db.commit()
        return UserResponse.model_validate(existing_user)

    raw_password = review.temporary_password or "JalDrishti@2026"
    new_user = User(
        name=req.name,
        email=req.email,
        password_hash=hash_password(raw_password),
        role=req.requested_role,
        state_id=req.state_id,
        district_id=req.district_id,
        organization=req.organization,
        designation=req.designation,
        is_active=True
    )
    db.add(new_user)
    
    req.status = "APPROVED"
    req.reviewed_by = int(current_admin.user_id) if current_admin.user_id.isdigit() else None
    req.reviewed_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(new_user)

    log_audit_event(
        db, action="ACCESS_REQUEST_APPROVED", resource_type="ACCESS_REQUEST",
        resource_id=str(req.id), user_id=current_admin.user_id,
        details={"provisioned_user_id": new_user.id, "email": new_user.email, "role": new_user.role},
        ip_address=client_ip
    )

    return UserResponse.model_validate(new_user)

@router.post("/access-requests/{request_id}/reject", response_model=AccessRequestResponse, summary="Reject access request")
def reject_access_request(
    request_id: int,
    review: AccessRequestReview,
    request: Request,
    current_admin: RequestUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Rejects an access request with recorded official administrative rationale."""
    client_ip = request.client.host if request.client else "unknown"

    req = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access request not found")

    if req.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject request with status '{req.status}'."
        )

    req.status = "REJECTED"
    req.rejection_reason = review.rejection_reason or "Administrative criteria not met"
    req.reviewed_by = int(current_admin.user_id) if current_admin.user_id.isdigit() else None
    req.reviewed_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(req)

    log_audit_event(
        db, action="ACCESS_REQUEST_REJECTED", resource_type="ACCESS_REQUEST",
        resource_id=str(req.id), user_id=current_admin.user_id,
        details={"email": req.email, "reason": req.rejection_reason},
        ip_address=client_ip
    )

    return AccessRequestResponse.model_validate(req)

# ==========================================
# Compliance & Audit Trail (Admin Only)
# ==========================================

@router.get("/audit-logs", response_model=List[AuditLogResponse], summary="List statutory audit log entries")
def list_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action: LOGIN_SUCCESS, USER_CREATED, etc."),
    resource_type: Optional[str] = Query(None, description="Filter by resource type: AUTH, USER, etc."),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_admin: RequestUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Returns statutory audit trail entries for national monitoring and compliance."""
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action.upper())
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type.upper())

    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    return [AuditLogResponse.model_validate(l) for l in logs]
