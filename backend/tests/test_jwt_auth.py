"""
JalDrishti AI — Stateless JWT Authentication & Role-Based Authorization Tests
Tests:
1. Successful login -> JWT returned with minimal claims (user_id, role, iat, exp)
2. Invalid credentials -> 401 (generic message without disclosing user existence)
3. Missing JWT -> 401 on protected endpoints
4. Invalid JWT -> 401
5. Expired JWT -> 401
6. Valid JWT -> protected endpoint accessible (200 OK)
7. Correct role -> allowed (200 OK)
8. Incorrect role -> 403 Forbidden
9. Existing watershed endpoint works with JWT (200 OK)
10. Existing reports endpoint works with JWT (200 OK)
11. Existing state hierarchy endpoint works with JWT (200 OK)
12. JWT claims minimal structure verification
"""

import datetime
import pytest
import jwt
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token

client = TestClient(app)

DEMO_PASSWORD = "JalDrishti@2026"

def login_and_get_token(email: str, password: str = DEMO_PASSWORD) -> str:
    """Helper to authenticate and return the stateless JWT token."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]

def test_1_successful_login_jwt_returned():
    """1. Successful login -> JWT returned with token_type bearer and valid profile."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@jaldrishti.gov.in", "password": DEMO_PASSWORD}
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@jaldrishti.gov.in"
    assert data["user"]["role"] == "ADMIN"

def test_2_invalid_credentials_returns_401():
    """2. Invalid credentials -> 401 with generic error message."""
    # Wrong password
    res_wrong_pw = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@jaldrishti.gov.in", "password": "WrongPassword123!"}
    )
    assert res_wrong_pw.status_code == 401
    assert "Invalid" in res_wrong_pw.json()["detail"]

    # Non-existent user
    res_no_user = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@department.gov.in", "password": "AnyPassword123!"}
    )
    assert res_no_user.status_code == 401
    assert "Invalid" in res_no_user.json()["detail"]

    # Identical error message so user existence is not revealed
    assert res_wrong_pw.json()["detail"] == res_no_user.json()["detail"]

def test_3_missing_jwt_returns_401():
    """3. Missing JWT -> 401 on protected endpoints."""
    # Explicitly clear authorization header
    headers = {"Authorization": ""}
    
    res_ws = client.get("/api/v1/watersheds", headers=headers)
    assert res_ws.status_code == 401

    res_states = client.get("/api/v1/states-hierarchy", headers=headers)
    assert res_states.status_code == 401

    res_reports = client.get("/api/v1/reports/1", headers=headers)
    assert res_reports.status_code == 401

def test_4_invalid_jwt_returns_401():
    """4. Invalid JWT -> 401."""
    headers = {"Authorization": "Bearer invalid.tampered.jwt.signature"}
    res = client.get("/api/v1/watersheds", headers=headers)
    assert res.status_code == 401
    assert "Could not validate credentials" in res.json()["detail"]

def test_5_expired_jwt_returns_401():
    """5. Expired JWT -> 401."""
    # Generate token already expired 10 minutes ago
    expired_token = create_access_token(
        data={"user_id": 1, "role": "ADMIN", "sub": "1"},
        expires_delta=datetime.timedelta(minutes=-10)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    res = client.get("/api/v1/watersheds", headers=headers)
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()

def test_6_valid_jwt_protected_endpoint_accessible():
    """6. Valid JWT -> protected endpoint accessible (200 OK)."""
    token = login_and_get_token("analyst@nrsc.isro.gov.in")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/watersheds", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

def test_7_correct_role_allowed():
    """7. Correct role (ADMIN accessing /api/v1/admin/users) -> allowed (200 OK)."""
    admin_token = login_and_get_token("admin@jaldrishti.gov.in")
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/admin/users", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

def test_8_incorrect_role_returns_403():
    """8. Incorrect role (FIELD_OFFICER accessing /api/v1/admin/users) -> 403 Forbidden."""
    field_token = login_and_get_token("field.hiware@ahmednagar.gov.in")
    headers = {"Authorization": f"Bearer {field_token}"}
    res = client.get("/api/v1/admin/users", headers=headers)
    assert res.status_code == 403
    assert "Access forbidden" in res.json()["detail"]

def test_9_existing_watershed_endpoint_works_with_jwt():
    """9. Existing watershed endpoint works with JWT (200 OK)."""
    token = login_and_get_token("analyst@nrsc.isro.gov.in")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/watersheds", headers=headers)
    assert res.status_code == 200
    watersheds = res.json()
    assert any("Hiware Bazar" in w["name"] for w in watersheds)

def test_10_existing_reports_endpoint_works_with_jwt():
    """10. Existing reports endpoint works with JWT (200 OK)."""
    token = login_and_get_token("analyst@nrsc.isro.gov.in")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/reports/1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "watershed" in data
    assert data["watershed"]["id"] == 1

def test_11_existing_state_hierarchy_endpoint_works_with_jwt():
    """11. Existing state hierarchy endpoint works with JWT (200 OK)."""
    token = login_and_get_token("analyst@nrsc.isro.gov.in")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/states-hierarchy", headers=headers)
    assert res.status_code == 200
    states = res.json()
    assert len(states) >= 1
    state_names = [s["name"] for s in states]
    assert "Maharashtra" in state_names

def test_12_jwt_claims_minimal_structure():
    """12. JWT claims verify: contains only user_id, role, iat, exp (and sub)."""
    token = login_and_get_token("analyst@nrsc.isro.gov.in")
    claims = decode_access_token(token)
    assert "user_id" in claims
    assert "role" in claims
    assert "iat" in claims
    assert "exp" in claims
    assert claims["role"] == "ANALYST"
    # Verify no session/refresh claims
    assert "session_id" not in claims
    assert "refresh" not in claims

def test_13_jwt_secret_production_fail_fast(monkeypatch):
    """Verify that in production, missing JWT_SECRET fails fast with RuntimeError and does NOT use default SECRET_KEY."""
    from app.core.config import Settings
    
    # 1. Production with explicit JWT_SECRET succeeds
    prod_with_secret = Settings(ENVIRONMENT="production", DEBUG=False, JWT_SECRET="custom_prod_secret_12345")
    assert prod_with_secret.jwt_secret_key == "custom_prod_secret_12345"

    # 2. Production without JWT_SECRET raises RuntimeError
    prod_missing_secret = Settings(ENVIRONMENT="production", DEBUG=False, JWT_SECRET=None)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="CRITICAL SECURITY CONFIGURATION ERROR"):
        _ = prod_missing_secret.jwt_secret_key

    # 3. Development without JWT_SECRET returns dev fallback key
    dev_settings = Settings(ENVIRONMENT="development", DEBUG=True, JWT_SECRET=None)
    assert "dev-insecure" in dev_settings.jwt_secret_key

def test_14_demo_accounts_contain_no_real_production_secrets():
    """Verify that public demo accounts catalog contains only clearly labeled prototype evaluator accounts."""
    res = client.get("/api/v1/auth/demo-accounts")
    assert res.status_code == 200
    accounts = res.json()
    assert len(accounts) == 5
    for acc in accounts:
        assert acc["demo_password"] == "JalDrishti@2026"
        assert "password_hash" not in acc
        assert "secret" not in acc
        assert "token" not in acc


def test_15_non_gov_demo_user_registration_active_immediately_and_can_login():
    """Verify non-government / team demo user registration is active immediately and can log in without admin approval."""
    from app.core.database import SessionLocal
    from app.models.domain import User

    unique_email = f"demo.team_{datetime.datetime.now().timestamp()}@example.com"
    reg_password = "DemoTeamUserPassword@2026"

    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Demo Evaluator User",
            "email": unique_email,
            "organization": "Technical Evaluation Team",
            "state_id": 1,
            "district_id": 1,
            "requested_role": "ANALYST",
            "password": reg_password,
            "confirm_password": reg_password
        }
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["status"] == "ACTIVE"
    assert "active" in reg_data["message"].lower()

    # Verify user in database is active
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == unique_email).first()
        assert user is not None
        assert user.is_active is True
        assert user.role == "ANALYST"
    finally:
        db.close()

    # Verify user can log in immediately after registration
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": reg_password}
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["email"] == unique_email
    assert token_data["user"]["is_active"] is True

    # Verify that the newly registered user can access protected endpoints with their token
    auth_header = {"Authorization": f"Bearer {token_data['access_token']}"}
    protected_res = client.get("/api/v1/watersheds", headers=auth_header)
    assert protected_res.status_code == 200


