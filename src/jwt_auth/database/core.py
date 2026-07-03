from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session as ORM_Session
from sqlalchemy.orm import scoped_session, sessionmaker

from src.jwt_auth import settings


class DatabaseManager:

    def __init__(self):
        self.db = settings.database
        self.engine = None
        self.Session = None
        self._init_engine()

    def _init_engine(self):
        connection_string = (
            f"mysql+pymysql://{self.db.user}:{self.db.password}@{self.db.host}/{self.db.database}"
        )

        self.engine = create_engine(
            connection_string,
            pool_size=30,
            max_overflow=50,
            pool_pre_ping=True,
            pool_recycle=1800,
            echo=False,
            pool_reset_on_return="rollback",
        )

        self.Session = scoped_session(sessionmaker(bind=self.engine))

    @contextmanager
    def session_scope(self) -> Generator[ORM_Session, None, None]:
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_session(self) -> ORM_Session:
        return self.Session()


manager = DatabaseManager()

engine = manager.engine
Base = declarative_base()
