from app.extensions import db
from ...ropp_service import Result
from ...mixins.authentication_mixin import AuthenticationMixin
from app.models import Course


class CreateCourse(AuthenticationMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]

        # Validate json fields
        required_fields = [
            "name",
            "description",
            "is_hidden",
            "image_url",
            "theories",
            "problems",
        ]
        for field in required_fields:
            if field not in raw_json:
                return Result(
                    success=False, error=f"{field} is required", error_code=400
                )

        input_data.update(raw_json)

        return Result.ok(input_data)

    @staticmethod
    def validate_course_data(input_data) -> Result:
        if not isinstance(input_data["name"], str) or not (
            1 <= len(input_data["name"]) <= 100
        ):
            return Result.fail(
                error="Name must be a string between 1 and 100 characters",
                error_code=400,
            )
        if not isinstance(input_data["description"], str) or not (
            1 <= len(input_data["description"]) <= 2000
        ):
            return Result.fail(
                error="Description must be a string between 1 and 2000 characters",
                error_code=400,
            )

        # Handle tags_json - make it optional
        # tags_json = input_data.get("tags_json", [])
        # if not isinstance(tags_json, str):
        #     return Result.fail(
        #         error="tags_json must be a string",
        #         error_code=400,
        #     )
        # input_data["tags_json"] = tags_json.split(",")
        # if not isinstance(input_data["difficulty"], str):
        #     return Result.fail(error="Difficulty must be a string", error_code=400)
        # if not isinstance(input_data["language"], str):
        #     return Result.fail(error="Language must be a string", error_code=400)

        return Result.ok(input_data)

    @staticmethod
    def execute(input_data) -> Result:
        current_user = input_data["current_user"]
        new_course = Course(
            name=input_data["name"],
            description=input_data["description"],
            image_url=input_data["image_url"],
            is_hidden=input_data["is_hidden"],
            theories=input_data["theories"],
            problems=input_data["problems"],
            author_id=current_user.id,
        )

        db.session.add(new_course)
        db.session.commit()
        return Result.ok({"course": new_course})

    @staticmethod
    def format(input_data) -> Result:
        course = input_data["course"]
        return Result.ok(
            data={
                "id": course.id,
                "name": course.name,
                "description": course.description,
                "image_url": course.image_url,
                "is_hidden": course.is_hidden,
                "theories": course.theories,
                "problems": course.problems,
                "author_id": course.author_id,
                "created_at": (
                    course.created_at.isoformat() if course.created_at else None
                ),
            },
        )
