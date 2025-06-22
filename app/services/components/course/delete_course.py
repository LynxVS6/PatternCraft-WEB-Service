from app.extensions import db
from ...ropp_service import Result
from ...mixins.authentication_mixin import AuthenticationMixin


class DeleteCourse(AuthenticationMixin):
    @staticmethod
    def execute(input_data):
        comment = input_data["comment"]
        db.session.delete(comment)
        db.session.commit()
        return Result.ok(input_data)

    @staticmethod
    def format(input_data):
        return Result.ok(
            data={"message": "Comment was successfully deleted!"},
        )
