from app.extensions import db
from ...ropp_service import Result
from ...mixins.authentication_mixin import AuthenticationMixin
from app.models import Theory
import base64


class CreateTheory(AuthenticationMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]

        # Validate task data
        required_fields = [
            "name",
            "description",
            "image",
            "content",
            "is_hidden"
        ]
        for field in required_fields:
            if field not in raw_json:
                return Result(
                    success=False, error=f"{field} is required", error_code=400
                )

        input_data["status"] = "beta"  # remove when status logic added
        input_data.update(raw_json)

        return Result.ok(input_data)

    @staticmethod
    def validate_create_data(input_data) -> Result:
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

        return Result.ok(input_data)

    @staticmethod
    def execute(input_data) -> Result:
        current_user = input_data["current_user"]
        new_theory = Theory(
            name=input_data["name"],
            description=input_data["description"],
            content=input_data["content"],
            image_url='',
            is_hidden=input_data["is_hidden"],
            author_id=current_user.id
        )

        db.session.add(new_theory)
        db.session.commit()

        print('[DEBUG] New theory created:', new_theory.id)

        if input_data['image'].startswith('data:image/'):
            filename = 'app/static/img/theories/' + str(new_theory.id) + '.png'
            base64_data = input_data["image"].split(',')[1]
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(base64_data))
        else:
            image_url = input_data["image"]
            new_theory.image_url = image_url
        
        db.session.commit()

        return Result.ok({"theory": new_theory})

    @staticmethod
    def format(input_data) -> Result:
        theory = input_data["theory"]
        return Result.ok(
            data={
                "id": theory.id,
                "name": theory.name,
                "description": theory.description,
                "content": theory.content,
                "image_url": theory.image_url,
                "is_hidden": theory.is_hidden,
                "author_id": theory.author_id,
                "created_at": (
                    theory.created_at.isoformat() if theory.created_at else None
                ),
            },
        )
