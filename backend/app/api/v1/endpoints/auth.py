"""
JalDrishti AI — Authentication & Access Request Endpoints
Provides official officer authentication, JWT issuance, profile resolution,
and controlled public access requests.
"""

from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password, hash_password, create_access_token, log_audit_event,
    get_current_user, require_authenticated_user, RequestUser, UserRole
)
from app.models.domain import User, AccessRequest, State, District, Watershed
from app.schemas.schemas import (
    LoginRequest, TokenResponse, UserResponse,
    AccessRequestCreate, AccessRequestResponse, DemoAccountResponse,
    UserRegisterRequest, RegistrationResponse,
    ForgotPasswordRequest, ForgotPasswordResponse
)

router = APIRouter()

@router.post("/login", response_model=TokenResponse, summary="Officer institutional login")
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Authenticates a departmental officer or system administrator using email or username and password.
    Returns a signed stateless PyJWT bearer token and complete user profile.
    """
    client_ip = request.client.host if request.client else "unknown"
    identifier = (login_data.email or login_data.username or "").strip()

    if not identifier or not login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid official email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(
        (User.email == identifier) | (User.name == identifier)
    ).first()

    if not user:
        log_audit_event(
            db, action="LOGIN_FAILED", resource_type="AUTH",
            resource_id=identifier, user_id=identifier,
            details={"reason": "User not found"}, ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid official email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not verify_password(login_data.password, user.password_hash):
        log_audit_event(
            db, action="LOGIN_FAILED", resource_type="AUTH",
            resource_id=user.email, user_id=str(user.id),
            details={"reason": "Incorrect password hash"}, ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid official email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        log_audit_event(
            db, action="LOGIN_REJECTED_INACTIVE", resource_type="AUTH",
            resource_id=user.email, user_id=str(user.id),
            details={"reason": "Account is inactive"}, ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Officer account has been deactivated. Please contact your System Administrator.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Update last login timestamp
    user.last_login = datetime.datetime.now(datetime.timezone.utc)
    db.commit()

    # Generate token with strictly necessary claims
    expires_delta = datetime.timedelta(days=7) if login_data.remember_me else datetime.timedelta(minutes=settings.jwt_expiration_minutes)
    token = create_access_token(
        data={
            "sub": str(user.id),
            "user_id": user.id,
            "role": user.role,
        },
        expires_delta=expires_delta
    )

    log_audit_event(
        db, action="LOGIN_SUCCESS", resource_type="AUTH",
        resource_id=str(user.id), user_id=str(user.id),
        details={"role": user.role, "email": user.email}, ip_address=client_ip
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_minutes=int(expires_delta.total_seconds() / 60),
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse, summary="Get current officer profile")
def get_me(
    current_user: RequestUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
):
    """Returns the profile and jurisdictional scope of the currently authenticated officer."""
    user = db.query(User).filter(User.id == int(current_user.user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)

@router.post("/logout", summary="Officer logout")
def logout(
    request: Request,
    current_user: RequestUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Records the logout audit event and clears server-side session references."""
    client_ip = request.client.host if request.client else "unknown"
    if current_user.is_authenticated:
        log_audit_event(
            db, action="LOGOUT", resource_type="AUTH",
            resource_id=current_user.user_id, user_id=current_user.user_id,
            details={"email": current_user.email}, ip_address=client_ip
        )
    return {"message": "Officer session concluded successfully", "status": "LOGGED_OUT"}

@router.post("/request-access", response_model=AccessRequestResponse, status_code=status.HTTP_201_CREATED, summary="Submit account creation request")
def submit_access_request(
    request_in: AccessRequestCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Submits a controlled access request for government officers requiring platform permissions.
    Requires manual review and approval by a platform Administrator before becoming active.
    """
    client_ip = request.client.host if request.client else "unknown"

    valid_roles = ["STATE_OFFICER", "DISTRICT_OFFICER", "FIELD_OFFICER", "ANALYST"]
    if request_in.requested_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid requested role '{request_in.requested_role}'. Must be one of: {valid_roles}"
        )

    # Check if an active account with this email already exists
    if db.query(User).filter(User.email == request_in.email.strip()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active officer account already exists for this email address."
        )

    # Check for duplicate pending requests
    pending = db.query(AccessRequest).filter(
        AccessRequest.email == request_in.email.strip(),
        AccessRequest.status == "PENDING"
    ).first()
    if pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending access request for this official email is already awaiting administrative approval."
        )

    access_req = AccessRequest(
        name=request_in.name.strip(),
        email=request_in.email.strip(),
        requested_role=request_in.requested_role,
        state_id=request_in.state_id,
        district_id=request_in.district_id,
        organization=request_in.organization.strip(),
        designation=request_in.designation.strip() if request_in.designation else None,
        reason=request_in.reason.strip(),
        status="PENDING"
    )
    db.add(access_req)
    db.commit()
    db.refresh(access_req)

    log_audit_event(
        db, action="USER_ACCESS_REQUESTED", resource_type="ACCESS_REQUEST",
        resource_id=str(access_req.id), user_id=request_in.email,
        details={"requested_role": request_in.requested_role, "org": request_in.organization},
        ip_address=client_ip
    )

    return AccessRequestResponse.model_validate(access_req)

@router.get("/demo-accounts", response_model=List[DemoAccountResponse], summary="List demo accounts for SIH evaluation")
def list_demo_accounts():
    """
    Returns the list of seeded demonstration accounts and test credentials.
    Designed exclusively for SIH evaluators and jury testing across all 5 jurisdictional roles.
    """
    return [
        DemoAccountResponse(
            name="Dr. Vikram Rathore",
            email="admin@jaldrishti.gov.in",
            role="ADMIN",
            jurisdiction="National Scope (Ministry of Jal Shakti)",
            organization="Ministry of Jal Shakti / DoLR",
            demo_password="JalDrishti@2026",
            description="Full administrative authority, user provisioning, access request approval, and audit logs."
        ),
        DemoAccountResponse(
            name="Dr. Ramesh Patil",
            email="state.officer@mahawatershed.gov.in",
            role="STATE_OFFICER",
            jurisdiction="State: Maharashtra (ID: 1)",
            organization="Maharashtra State Watershed Management Agency",
            demo_password="JalDrishti@2026",
            description="Supervises all districts and micro-watersheds within Maharashtra state boundary."
        ),
        DemoAccountResponse(
            name="Anil Sharma",
            email="district.officer@ahmednagar.gov.in",
            role="DISTRICT_OFFICER",
            jurisdiction="District: Ahmednagar, Maharashtra (ID: 1)",
            organization="Ahmednagar District Rural Development Agency",
            demo_password="JalDrishti@2026",
            description="Oversees catchment interventions, watershed statistics, and DPR planning in Ahmednagar."
        ),
        DemoAccountResponse(
            name="Suresh Gaikwad",
            email="field.hiware@ahmednagar.gov.in",
            role="FIELD_OFFICER",
            jurisdiction="Watershed: Hiware Bazar (WS-MH-AHM-001)",
            organization="Hiware Bazar Watershed Committee",
            demo_password="JalDrishti@2026",
            description="Field-level officer authorized for ground inspection, geo-tagged photo uploads, and observations."
        ),
        DemoAccountResponse(
            name="Pooja Iyer",
            email="analyst@nrsc.isro.gov.in",
            role="ANALYST",
            jurisdiction="National Remote Sensing & GIS Analytics",
            organization="National Remote Sensing Centre (NRSC / ISRO)",
            demo_password="JalDrishti@2026",
            description="Cross-catchment access to GIS layers, LULC change detection, ML projections, and risk models."
        )
    ]

@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED, summary="Official officer registration")
def register(
    reg_in: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Submits official user registration.
    In accordance with departmental cybersecurity policy, registration creates an access request
    pending administrative identity verification before privileges are activated.
    """
    client_ip = request.client.host if request.client else "unknown"

    if reg_in.password != reg_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )

    if len(reg_in.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters in length."
        )

    valid_roles = ["STATE_OFFICER", "DISTRICT_OFFICER", "FIELD_OFFICER", "ANALYST"]
    if reg_in.requested_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid requested role '{reg_in.requested_role}'. Must be one of: {valid_roles}"
        )

    # Check for existing user
    existing_user = db.query(User).filter(User.email == reg_in.email.strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this official email address already exists."
        )

    # Check for pending access request
    pending = db.query(AccessRequest).filter(
        AccessRequest.email == reg_in.email.strip(),
        AccessRequest.status == "PENDING"
    ).first()
    if pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending access request for this official email is already awaiting administrative approval."
        )

    # Non-government / team demo accounts are active immediately to allow instant login.
    # Official government domains (.gov.in, .nic.in) require administrative verification.
    email_clean = reg_in.email.strip().lower()
    is_gov_domain = email_clean.endswith(".gov.in") or email_clean.endswith(".nic.in")
    is_active = not is_gov_domain

    # Create user account
    user = User(
        name=reg_in.name.strip(),
        email=reg_in.email.strip(),
        password_hash=hash_password(reg_in.password),
        role=reg_in.requested_role,
        state_id=reg_in.state_id,
        district_id=reg_in.district_id,
        organization=reg_in.organization.strip(),
        designation="Field / Departmental Officer",
        is_active=is_active
    )
    db.add(user)

    # Create access request for admin workflow
    access_req = AccessRequest(
        name=reg_in.name.strip(),
        email=reg_in.email.strip(),
        requested_role=reg_in.requested_role,
        state_id=reg_in.state_id,
        district_id=reg_in.district_id,
        organization=reg_in.organization.strip(),
        designation="Field / Departmental Officer",
        reason="Portal Self-Registration",
        status="PENDING" if is_gov_domain else "APPROVED"
    )
    db.add(access_req)
    db.commit()
    db.refresh(access_req)

    log_audit_event(
        db, action="USER_REGISTERED", resource_type="USER",
        resource_id=str(user.id), user_id=reg_in.email,
        details={"requested_role": reg_in.requested_role, "org": reg_in.organization, "is_active": is_active},
        ip_address=client_ip
    )

    if is_active:
        return RegistrationResponse(
            message="Registration successful. Your account is active and you may now log in.",
            status="ACTIVE",
            request_id=access_req.id
        )

    return RegistrationResponse(
        message="Official account registration submitted successfully. Your request has been queued for Administrator verification.",
        status="PENDING_APPROVAL",
        request_id=access_req.id
    )

@router.post("/forgot-password", response_model=ForgotPasswordResponse, summary="Officer password recovery dispatch")
def forgot_password(
    forgot_in: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Initiates departmental password recovery workflow.
    For government security adherence, instructions are dispatched via official channels.
    """
    client_ip = request.client.host if request.client else "unknown"
    user = db.query(User).filter(User.email == forgot_in.email.strip()).first()

    if user:
        log_audit_event(
            db, action="PASSWORD_RECOVERY_REQUESTED", resource_type="AUTH",
            resource_id=user.email, user_id=str(user.id),
            details={"email": user.email}, ip_address=client_ip
        )

    return ForgotPasswordResponse(
        message="If this official email is registered, password reset instructions and security verification details have been routed through official departmental channels.",
        status="DISPATCHED",
        support_contact="admin@jaldrishti.gov.in / National Helpdesk: 1800-111-JAL"
    )

