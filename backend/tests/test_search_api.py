"""Regression tests for authenticated search accounting and source metadata."""
import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-that-is-long-enough-for-jwt-signing")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.routes import _query_cache, _transform_sources_optimized, router
from auth import models, security
from auth.database import Base, get_db


class FakeRAGEngine:
    def ask(self, *_args):
        return {
            "answer": "Grounded answer [Source 1]",
            "num_sources": 1,
            "search_time": 0.01,
            "generation_time": 0.01,
            "sources": [
                {
                    "score": 0.8,
                    "full_text": "Example v. Florida, 123 U.S. 456 (2020).",
                    "source": "Example v. Florida",
                    "collection": "legal_cases",
                    "metadata": {
                        "court": "Florida Supreme Court",
                        "date_filed": "2020-01-01",
                        "citation": "123 U.S. 456",
                        "url": "https://example.test/case",
                    },
                    "citations": [
                        {
                            "type": "us_reporter",
                            "text": "123 U.S. 456",
                            "link": "https://www.courtlistener.com/c/us/123/456/",
                            "position": 20,
                        }
                    ],
                }
            ],
        }


def make_app(search_count=0, authenticated=True):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(engine)
    db = TestingSession()
    user = models.User(
        email="researcher@example.com",
        hashed_password="unused",
        tier="free",
        search_count=search_count,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    app = FastAPI()
    app.state.rag_engine = FakeRAGEngine()
    app.include_router(router, prefix="/api/v1")

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    if authenticated:
        app.dependency_overrides[security.get_current_active_user] = lambda: user

    return app, db, user


def setup_function():
    _query_cache.clear()


def test_search_requires_authentication():
    app, db, _user = make_app(authenticated=False)
    try:
        response = TestClient(app).post(
            "/api/v1/search",
            json={"query": "Florida contract law", "collection": "cases"},
        )
        assert response.status_code == 401
    finally:
        db.close()


def test_search_atomically_counts_usage_and_preserves_metadata():
    app, db, user = make_app(search_count=14)
    client = TestClient(app)
    try:
        response = client.post(
            "/api/v1/search",
            json={"query": "Florida contract law", "collection": "cases"},
        )
        assert response.status_code == 200
        assert response.headers["cache-control"] == "private, no-store"
        assert response.json()["metadata"]["searches_remaining"] == 0
        assert response.json()["sources"][0]["metadata"]["court"] == "Florida Supreme Court"
        assert response.json()["sources"][0]["citations"][0]["text"] == "123 U.S. 456"

        db.refresh(user)
        assert user.search_count == 15
        assert db.query(models.SearchHistory).count() == 1

        blocked = client.post(
            "/api/v1/search",
            json={"query": "A different legal question", "collection": "cases"},
        )
        assert blocked.status_code == 403
        db.refresh(user)
        assert user.search_count == 15
    finally:
        db.close()


def test_failed_search_refunds_reserved_usage():
    app, db, user = make_app(search_count=3)

    class BrokenRAGEngine:
        def ask(self, *_args):
            raise RuntimeError("external service unavailable")

    app.state.rag_engine = BrokenRAGEngine()
    try:
        response = TestClient(app).post(
            "/api/v1/search",
            json={"query": "Federal contract law", "collection": "cases"},
        )
        assert response.status_code == 500
        assert response.json()["detail"] == "Search failed. Please try again."
        db.refresh(user)
        assert user.search_count == 3
    finally:
        db.close()


def test_state_query_transformation_does_not_reference_court_before_assignment():
    transformed = _transform_sources_optimized(
        [
            {
                "score": 0.7,
                "full_text": "A Florida contract decision, 123 U.S. 456.",
                "metadata": {"court": "Florida Supreme Court"},
                "collection": "legal_cases",
            }
        ],
        "Florida contract requirements",
    )
    assert transformed[0]["metadata"]["court"] == "Florida Supreme Court"
    assert 0 <= transformed[0]["score"] <= 1


def test_search_request_validation_rejects_unknown_collection():
    app, db, _user = make_app()
    try:
        response = TestClient(app).post(
            "/api/v1/search",
            json={"query": "Valid legal query", "collection": "everything"},
        )
        assert response.status_code == 422
    finally:
        db.close()
