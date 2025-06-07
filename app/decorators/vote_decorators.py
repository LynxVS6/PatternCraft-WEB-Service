from functools import wraps
from typing import List, Callable, Any, Tuple
from flask import jsonify, request
from app.utils.validators import validate_vote_type

# Define vote types for different entities
VOTE_TYPES = {
    "problem": ["positive", "neutral", "negative"],
    "solution": ["like", "dislike"],
    "comment": ["up", "down"],
    "discourse": ["up", "down"],
}


def validate_vote_request(allowed_types: List[str]):
    """Decorator to validate vote request data and types."""

    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            is_valid, error = validate_vote_type(data, allowed_types)
            if not is_valid:
                return jsonify({"error": error}), 400

            # Add validated vote_type to kwargs
            kwargs["vote_type"] = data.get("vote_type")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def handle_vote_response():
    """Decorator to handle vote service response formatting."""

    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)

            if not result.success:
                if result.error_code == "NOT_FOUND":
                    return jsonify({"error": result.error}), 404
                return jsonify({"error": result.error}), 500

            return jsonify(result.data)

        return decorated_function

    return decorator


def with_vote_service(service_class):
    """Decorator to inject vote service into the function."""

    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            kwargs["vote_service"] = service_class
            return f(*args, **kwargs)

        return decorated_function

    return decorator
