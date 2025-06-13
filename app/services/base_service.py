from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from abc import ABC
from typing import Optional, Dict, Any, TypeVar, Generic

T = TypeVar("T")


class Result(Generic[T]):
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        error_code: Optional[int] = None,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.error_code = error_code

    def bind(self, func):  # Railway-Oriented Programming Pattern (ROP)
        if not self.success:
            return self
        return func(self.data)


class BaseService(ABC):
    @staticmethod
    def _handle_errors(func):
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
                    success=False,
                    error=f"Database error: {str(e)}",
                    error_code=500,
                )
            except Exception as e:
                db.session.rollback()
                return Result(
                    success=False,
                    error=f"Unexpected error: {str(e)}",
                    error_code=500,
                )

        return wrapper

    @staticmethod
    def _parse_errors(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TypeError as e:
                return Result(
                    False,
                    error=f"Invalid input format: {str(e)}",
                    error_code=400,
                )
            except KeyError as e:
                return Result(
                    False,
                    error=f"Missing required field: {str(e)}",
                    error_code=400,
                )

        return wrapper

    @staticmethod
    def _process_input_data(
        input_data, parse_func, validation_func, handle_func, sending_func
    ) -> Result:
        return (
            Result(
                True,
                data=input_data,
            )
            .bind(parse_func)
            .bind(validation_func)
            .bind(handle_func)
            .bind(sending_func)
        )

    @staticmethod
    def _get_target(input_data) -> Result:
        target_model = input_data.get("target_model")
        target_id = input_data.get("target_id")
        target = target_model.query.get(target_id)
        if not target:
            return Result(
                success=False,
                error=f"Target model with id {target_id} not found",
                error_code=400,
            )
        else:
            input_data.update({"target": target})
            return Result(success=True, data=input_data)

    @staticmethod
    def _combine_funcs(*funcs):
        """Combine multiple validators into a single function for ROP chaining."""

        def combined(data):
            for func in funcs:
                result = func(data)
                if not result.success:
                    return result
            return Result(success=True, data=data)

        return combined
