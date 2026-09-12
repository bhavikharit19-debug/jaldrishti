import pytest
from app.core.security import create_access_token
from app.models.domain import User
from app.core.database import SessionLocal

@pytest.fixture(autouse=True)
def setup_test_auth(request):
    """
    Ensures existing integration test suites (test_api.py, test_api_step3.py, etc.)
    have a valid Bearer token attached to their module-level TestClient,
    while auth test suites (test_auth_rbac.py, test_jwt_auth.py) manage their own headers.
    """
    module = getattr(request, "module", None)
    if not module:
        yield
        return

    module_name = getattr(module, "__name__", "")
    client = getattr(module, "client", None)

    if not client:
        yield
        return

    # If the test is specifically in auth/rbac test suites, ensure clean headers unless set by test
    if "auth" in module_name.lower():
        old_auth = client.headers.pop("Authorization", None)
        yield
        if old_auth:
            client.headers["Authorization"] = old_auth
        return

    # For legacy integration suites (test_api, test_gis, test_ml, test_data_pipeline):
    # generate a valid admin bearer token so all protected data endpoints work seamlessly
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin@jaldrishti.gov.in").first()
        user_id = admin_user.id if admin_user else 1
    finally:
        db.close()

    token = create_access_token(data={"user_id": user_id, "role": "ADMIN", "sub": str(user_id)})
    prev_auth = client.headers.get("Authorization")
    client.headers["Authorization"] = f"Bearer {token}"
    yield
    if prev_auth is not None:
        client.headers["Authorization"] = prev_auth
    else:
        client.headers.pop("Authorization", None)
