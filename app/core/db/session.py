from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app.core.config import get_settings

from .base import Base

import logging

# Setup logger
logging.basicConfig()
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)

# Hide default SQLAlchemy noise
logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

class DBSession:
    """DB Session."""
    engine = create_engine(get_settings().DATABASE_URL, echo=False, pool_pre_ping=True)

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        try:
            query = statement % parameters
            logger.info("🚀 Executing SQL:\n%s", query)
        except Exception:
            logger.info("⚠️ Raw SQL: %s", statement)
            logger.info("🔢 Parameters: %s", parameters)

    @lru_cache
    def create_session(self) -> scoped_session:
        """DB Session Creation."""
        Session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        return Session

    def get_session(self) -> Generator[scoped_session, None, None]:
        """Get DB Session."""
        db = self.create_session()
        try:
            yield db
        except:
            db.remove()


session = DBSession()
