"""
JalDrishti AI — Step 6 Automated Test Suite: Authentication & Role-Based Access Control (RBAC)
Covers login, JWT issuance, profile resolution, role authorization,
jurisdictional boundaries, user provisioning, access request lifecycle, and audit logs.
"""

import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.domain import User, AccessRequest, AuditLog, FieldPhoto
from app.core.security import hash_password

client = TestClient(app)

DEMO_PASSWORD = "JalDrishti@2026"

def get_auth_token(email: str, password: str = DEMO_PASSWORD) -> str:
    """Helper to authenticate and return a bearer token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200, f"Failed to login as {email}: {response.text}"
    return response.json()["access_token"]

def test_demo_accounts_endpoint():
    """Verify the demo accounts public catalog endpoint for SIH evaluators."""
    response = client.get("/api/v1/auth/demo-accounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    roles = {u["role"] for u in data}
    assert roles == {"ADMIN", "STATE_OFFICER", "DISTRICT_OFFICER", "FIELD_OFFICER", "ANALYST"}
    for acc in data:
        assert acc["demo_password"] == DEMO_PASSWORD

def test_successful_login():
    """Verify successful login returns valid JWT token and user profile."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@jaldrishti.gov.in", "password": DEMO_PASSWORD}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@jaldrishti.gov.in"
    assert data["user"]["role"] == "ADMIN"
    assert data["user"]["is_active"] is True

def test_invalid_password_returns_401():
    """Verify incorrect password results in 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@jaldrishti.gov.in", "password": "WrongPassword123!"}
    )
    assert response.status_code == 401
    assert "Invalid official email or password" in response.json()["detail"]

def test_unknown_user_returns_401():
    """Verify unknown user results in 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent.officer@gov.in", "password": "AnyPassword"}
    )
    assert response.status_code == 401

def test_deactivated_account_rejected():
    """Verify inactive user cannot authenticate."""
    db = SessionLocal()
    try:
        # Create a temporarily deactivated officer
        temp_user = User(
            name="Deactivated Officer",
            email="deactivated.test@jaldrishti.gov.in",
            password_hash=hash_password("TempPass@123"),
            role="FIELD_OFFICER",
            is_active=False
        )
        db.add(temp_user)
        db.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "deactivated.test@jaldrishti.gov.in", "password": "TempPass@123"}
        )
        assert response.status_code == 401
        assert "deactivated" in response.json()["detail"].lower()

        # Cleanup
        db.delete(temp_user)
        db.commit()
    finally:
        db.close()

def test_get_current_user_me():
    """Verify /auth/me returns the authenticated profile from Bearer token."""
    token = get_auth_token("analyst@nrsc.isro.gov.in")
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "analyst@nrsc.isro.gov.in"
    assert data["role"] == "ANALYST"
    assert "NRSC" in data["organization"]

def test_unauthenticated_me_returns_401():
    """Verify /auth/me rejects unauthenticated callers."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_invalid_token_returns_401():
    """Verify malformed or invalid token is rejected."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.token.string"}
    )
    assert response.status_code == 401

def test_admin_role_authorization():
    """Verify admin-only operations enforce role authorization."""
    admin_token = get_auth_token("admin@jaldrishti.gov.in")
    field_token = get_auth_token("field.hiware@ahmednagar.gov.in")

    # Admin accesses user list -> 200 OK
    resp_admin = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_admin.status_code == 200
    assert len(resp_admin.json()) >= 5

    # Field officer attempts admin user list -> 403 Forbidden
    resp_field = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {field_token}"}
    )
    assert resp_field.status_code == 403
    assert "Access forbidden" in resp_field.json()["detail"]

    # Unauthenticated caller -> 401 Unauthorized
    resp_anon = client.get("/api/v1/admin/users")
    assert resp_anon.status_code == 401

def test_access_request_and_approval_provisioning_flow():
    """
    Tests end-to-end user provisioning workflow:
    1. Public officer submits AccessRequest
    2. Admin reviews pending requests
    3. Admin approves request -> User account provisioned
    4. Newly provisioned user logs in successfully
    """
    admin_token = get_auth_token("admin@jaldrishti.gov.in")
    unique_email = "test.surveyor@rajwatershed.gov.in"

    # 1. Submit access request
    req_payload = {
        "name": "Kavita Rao",
        "email": unique_email,
        "requested_role": "FIELD_OFFICER",
        "state_id": 1,
        "district_id": 1,
        "organization": "Rajasthan Watershed Directorate",
        "designation": "Assistant Agronomist",
        "reason": "Official assignment to monitor micro-catchments under SIH 26015."
    }
    submit_resp = client.post("/api/v1/auth/request-access", json=req_payload)
    assert submit_resp.status_code == 201
    req_data = submit_resp.json()
    req_id = req_data["id"]
    assert req_data["status"] == "PENDING"

    # 2. Admin views pending requests
    list_resp = client.get(
        "/api/v1/admin/access-requests?status_filter=PENDING",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert list_resp.status_code == 200
    pending_ids = [r["id"] for r in list_resp.json()]
    assert req_id in pending_ids

    # 3. Admin approves request with temporary password
    approve_resp = client.post(
        f"/api/v1/admin/access-requests/{req_id}/approve",
        json={"action": "APPROVE", "temporary_password": "NewUserPass@2026"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert approve_resp.status_code == 200
    new_user = approve_resp.json()
    assert new_user["email"] == unique_email
    assert new_user["role"] == "FIELD_OFFICER"
    assert new_user["is_active"] is True

    # 4. Provisioned officer logs in with approved credentials
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "NewUserPass@2026"}
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # Cleanup test user & request
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == unique_email).delete()
        db.query(AccessRequest).filter(AccessRequest.id == req_id).delete()
        db.commit()
    finally:
        db.close()

def test_access_request_rejection_flow():
    """Verify administrative rejection of ineligible access request."""
    admin_token = get_auth_token("admin@jaldrishti.gov.in")
    unique_email = "ineligible.applicant@external.com"

    # Submit request
    submit_resp = client.post(
        "/api/v1/auth/request-access",
        json={
            "name": "External Party",
            "email": unique_email,
            "requested_role": "STATE_OFFICER",
            "organization": "Non-Government Agency",
            "reason": "General research interest"
        }
    )
    assert submit_resp.status_code == 201
    req_id = submit_resp.json()["id"]

    # Admin rejects
    reject_resp = client.post(
        f"/api/v1/admin/access-requests/{req_id}/reject",
        json={"action": "REJECT", "rejection_reason": "Applicant not a gazetted state officer."},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "REJECTED"
    assert reject_resp.json()["rejection_reason"] == "Applicant not a gazetted state officer."

    # Cleanup
    db = SessionLocal()
    try:
        db.query(AccessRequest).filter(AccessRequest.id == req_id).delete()
        db.commit()
    finally:
        db.close()

def test_field_officer_jurisdiction_scoping():
    """
    Verify field officer is permitted in assigned catchment (Hiware Bazar: watershed_id=1)
    and rejected when trying to upload into unassigned catchment (Ralegan Siddhi: watershed_id=2).
    """
    field_token = get_auth_token("field.hiware@ahmednagar.gov.in")

    # 1. Upload for assigned Watershed 1 (Allowed)
    with open("app/core/security.py", "rb") as f:
        content = f.read()
    
    # Send request with field officer token for Watershed 1
    resp_assigned = client.post(
        "/api/v1/photos/upload",
        data={
            "watershed_id": 1,
            "category": "WATER_BODY",
            "description": "Routine percolation tank inspection",
            "latitude": 19.05,
            "longitude": 74.60
        },
        files={"file": ("test_photo.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9", "image/jpeg")},
        headers={"Authorization": f"Bearer {field_token}"}
    )
    assert resp_assigned.status_code == 201

    # 2. Upload for Watershed 2 (Forbidden: Officer restricted to Watershed 1)
    resp_unassigned = client.post(
        "/api/v1/photos/upload",
        data={
            "watershed_id": 2,
            "category": "WATER_BODY",
            "description": "Attempted out-of-boundary upload",
            "latitude": 18.98,
            "longitude": 74.45
        },
        files={"file": ("test_photo.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9", "image/jpeg")},
        headers={"Authorization": f"Bearer {field_token}"}
    )
    assert resp_unassigned.status_code == 403
    assert "Jurisdictional access denied" in resp_unassigned.json()["detail"]

    # Cleanup test photo
    db = SessionLocal()
    try:
        db.query(FieldPhoto).filter(FieldPhoto.description == "Routine percolation tank inspection").delete()
        db.commit()
    finally:
        db.close()


def test_statutory_audit_logs():
    """Verify statutory audit trail records events and is accessible to Admin."""
    admin_token = get_auth_token("admin@jaldrishti.gov.in")
    response = client.get(
        "/api/v1/admin/audit-logs?limit=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) > 0
    actions = {l["action"] for l in logs}
    assert any(a in actions for a in ["LOGIN_SUCCESS", "SEED_PHASE2_GIS_LAYERS", "ACCESS_REQUEST_APPROVED", "USER_ACCESS_REQUESTED"])

def test_officer_logout():
    """Verify officer logout endpoint records audit event."""
    token = get_auth_token("analyst@nrsc.isro.gov.in")
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "LOGGED_OUT"

def test_user_registration():
    """Verify user registration queues an access request and creates inactive account."""
    unique_email = f"new.cadre_{datetime.datetime.utcnow().timestamp()}@department.gov.in"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Shri Rajesh Verma",
            "email": unique_email,
            "organization": "State Remote Sensing Applications Centre",
            "state_id": 1,
            "district_id": 1,
            "requested_role": "ANALYST",
            "password": "SecurePassword@2026",
            "confirm_password": "SecurePassword@2026"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "PENDING_APPROVAL"
    assert "request_id" in data

    # Verify inactive user exists
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == unique_email).first()
        assert user is not None
        assert user.is_active is False
        assert user.role == "ANALYST"
    finally:
        db.close()

def test_user_registration_mismatched_password():
    """Verify user registration fails with mismatched passwords."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Mismatch Test",
            "email": "mismatch@department.gov.in",
            "organization": "Dept",
            "requested_role": "ANALYST",
            "password": "Password123!",
            "confirm_password": "DifferentPassword!"
        }
    )
    assert response.status_code == 400
    assert "Passwords do not match" in response.json()["detail"]

def test_forgot_password_dispatch():
    """Verify forgot password returns institutional response."""
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "admin@jaldrishti.gov.in"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DISPATCHED"
    assert "1800-111-JAL" in data["support_contact"]

