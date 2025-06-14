from abc import ABC
from typing import Optional, Dict, TypeVar, Generic


class ROPPService(ABC):
    """Railway-Oriented Processing Pipeline Coordinator"""

    pass


T = TypeVar("T")


class Result(Generic[T]):
    def __init__(
        self,
        success: bool,
        data: Optional[T] = None,
        error: Optional[str] = None,
        error_code: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.error_code = error_code
        self.metadata = metadata or {}

    def bind(self, func, step_name: str = None):
        """ROP binding with execution tracking"""
        if not self.success:
            return self

        try:
            result = func(self.data)
            if step_name:
                result.metadata["steps"] = self.metadata.get("steps", []) + [step_name]
            return result
        except Exception as e:
            return Result.fail(
                error=str(e),
                error_code=getattr(e, "code", 500),
                metadata={
                    "failed_step": step_name,
                    "previous_steps": self.metadata.get("steps", []),
                },
            )

    @classmethod
    def ok(cls, data: Optional[T] = None, **metadata) -> "Result[T]":
        return cls(True, data=data, metadata=metadata)

    @classmethod
    def fail(cls, error: str, error_code: int = 400, **metadata) -> "Result[T]":
        return cls(False, error=error, error_code=error_code, metadata=metadata)


class RailwayService:
    @classmethod
    def execute_flow(cls, input_data, steps):
        """
        Execute a configurable railway flow.

        Args:
            steps: List of (function, step_name) tuples or just functions
        """
        result = Result.ok(input_data)

        for step in steps:
            if isinstance(step, tuple):
                func, step_name = step
            else:
                func, step_name = step, None

            result = result.bind(func, step_name)
            if not result.success:
                break

        return result
