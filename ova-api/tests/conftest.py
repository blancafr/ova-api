import os
import tempfile
import uuid
import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from datetime import date as d

from app.main import app
from app.db.user_database import Base as UserBase
from app.db.user_database import get_db as get_user_db_dep
from app.models.user import User

from app.db.registry_database import Base as RegistryBase
from app.db.registry_database import get_db as get_registry_db_dep
from app.models.registry import Registry
from app.main import app as fastapi_app
from app.auth.security import get_password_hash

@pytest.fixture(scope="session")
def user_db_url():
    fd, path = tempfile.mkstemp(prefix="users_test_", suffix=".sqlite")
    os.close(fd)
    url = f"sqlite:///{path}"
    try:
        yield url
    finally:
        try:
            os.remove(path)
        except PermissionError:
            pass

@pytest.fixture(scope="session")
def user_engine(user_db_url):
    eng = create_engine(user_db_url, connect_args={"check_same_thread": False})
    UserBase.metadata.create_all(eng)
    try:
        yield eng
    finally:
        eng.dispose()

@pytest.fixture
def user_session(user_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(user_session):
    def _override_user_get_db():
        try:
            yield user_session
        finally:
            pass

    app.dependency_overrides[get_user_db_dep] = _override_user_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def make_user(user_session):
    def _make_user(email: str, password: str, *, is_active=True, is_superuser=False, full_name=None):
        existing = user_session.query(User).filter_by(email=email).first()
        if existing:
            return existing
        u = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        user_session.add(u)
        user_session.commit()
        user_session.refresh(u)
        return u
    return _make_user


@pytest.fixture
def tokens(client, make_user):
    admin_email = f"admin+{uuid.uuid4().hex[:6]}@ova.org"
    user_email = f"user+{uuid.uuid4().hex[:6]}@ova.org"

    make_user(admin_email, "admin123", is_superuser=True)
    make_user(user_email, "user123", is_superuser=False)

    def login(email, password):
        data = {"username": email, "password": password}  # OAuth2PasswordRequestForm
        r = client.post("/users/login/access-token", data=data)
        assert r.status_code == 200, r.text
        return r.json()["access_token"]

    return SimpleNamespace(
        superuser=login(admin_email, "admin123"),
        regular=login(user_email, "user123"),
    )

@pytest.fixture(scope="session")
def registry_db_file():
    fd, path = tempfile.mkstemp(prefix="registry_test_", suffix=".sqlite")
    os.close(fd)
    try:
        yield path
    finally:
        try:
            os.remove(path)
        except PermissionError:
            pass

@pytest.fixture(scope="session")
def registry_engine(registry_db_file):
    url = f"sqlite:///{registry_db_file}"
    eng = create_engine(url, connect_args={"check_same_thread": False})
    RegistryBase.metadata.create_all(eng)
    try:
        yield eng
    finally:
        eng.dispose()

@pytest.fixture
def registry_session(registry_engine):
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=registry_engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client_with_registry_db(client, registry_session):
    def _override_registry_get_db():
        try:
            yield registry_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_registry_db_dep] = _override_registry_get_db
    try:
        yield client
    finally:
        fastapi_app.dependency_overrides.pop(get_registry_db_dep, None)


@pytest.fixture
def seed_registries(registry_session):
    registry_session.execute(text("DELETE FROM registry"))
    rows = [
        ("20250501", 1, d(2025, 5, 1),  "Hombre", ">50años", "malaria"),
        ("20250501", 2, d(2025, 5, 1),  "Hombre", ">50años", "malaria,hipertension"),
        ("20250501", 3, d(2025, 5, 1),  "Hombre", "15-49años", "diabetes"),

        ("20250502", 1, d(2025, 5, 2),  "Mujer", ">50años", "malaria"),
        ("20250502", 2, d(2025, 5, 2),  "Mujer", "15-49años", "malaria"),
        ("20250502", 3, d(2025, 5, 2),  "Mujer", "15-49años", "hipertension"),

        ("20250610", 1, d(2025, 6,10),  "Hombre", "15-49años", "malaria"),
        ("20250610", 2, d(2025, 6,10),  "Hombre", "15-49años", "malaria"),
        ("20250610", 3, d(2025, 6,10),  "Mujer", "15-49años", "diabetes"),

        ("20250611", 1, d(2025, 6,11),  "Mujer", ">50años", "malaria,diabetes"),
    ]

    for _id, row, _date, sex, age, diseases in rows:
        registry_session.add(Registry(
            id=_id, row_num=row, date=_date, sex=sex, age=age, diseases=diseases
        ))
    registry_session.commit()
