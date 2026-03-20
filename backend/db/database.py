from sqlmodel import create_engine, Session
from core.config import settings

# connect_args is only needed for SQLite (not thread-safe by default)
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,          # logs every SQL query when DEBUG=True
    connect_args=connect_args,
)


def get_session():
    """
    FastAPI dependency — yields a DB session and auto-closes it.

    Usage in a route:
        def my_route(db: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session