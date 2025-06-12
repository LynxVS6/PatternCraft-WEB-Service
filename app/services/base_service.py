from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from abc import ABC
from dataclasses import dataclass
from typing import Optional, Dict, Any, TypeVar, Generic

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[int] = None


class BaseService(ABC):
    @staticmethod
    def handle_errors(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                db.session.rollback()
                return Result(
                    success=False,
                    error=f"Database connection error: {str(e)}",
                    error_code=500,
                )
            except SQLAlchemyError as e:
                db.session.rollback()
                return Result(
                    success=False, error=f"Database error: {str(e)}", error_code=500
                )
            except Exception as e:
                db.session.rollback()
                return Result(
                    success=False, error=f"Unexpected error: {str(e)}", error_code=500
                )

        return wrapper
