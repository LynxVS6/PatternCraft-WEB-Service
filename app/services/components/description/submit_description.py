from app.extensions import db
from ...ropp_service import Result
from .description_author_mixin import DescriptionMixin


class SubmitDescription(DescriptionMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        description = raw_json.get("description")
        input_data["description"] = description
        return Result.ok(input_data)

    @staticmethod
    def validate_description_data(input_data) -> Result:
        description = input_data["description"]
        if description is None:
            return Result.fail(
                error="Description is required",
                error_code=400,
            )
        if not isinstance(description, str):
            return Result.fail(
                error="Description must be a string",
                error_code=400,
            )
        if not (1 <= len(description) <= 5000):
            return Result.fail(
                error="Description must be between 1 and 5000 characters",
                error_code=400,
            )
        return Result.ok(input_data)

    @staticmethod
    def execute(input_data):
        target = input_data["target"]
        description = input_data["description"]
        target.description = description
        db.session.commit()
        return Result.ok(input_data)

    @staticmethod
    def format(input_data):
        target_id = input_data["target_id"]
        description = input_data["description"]
        return Result.ok(
            data={
                "target_id": target_id,
                "description": description,
            },
        )
