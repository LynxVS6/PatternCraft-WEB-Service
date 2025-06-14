from ...ropp_service import Result
from .description_author_mixin import DescriptionMixin


class CheckAuth(DescriptionMixin):
    @staticmethod
    def format(input_data):
        return Result.ok(
            data={"message": "Authorized to edit description"},
        )
