import os
import pytest

from src import create_app
from src.database import db as _db


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test `Flask` application."""
    config_override = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ.get(
            "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/transtel"
        ),
    }
    app = create_app(config_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope="session")
def db(app, request):
    """Session-wide test database."""

    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="function")
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session
