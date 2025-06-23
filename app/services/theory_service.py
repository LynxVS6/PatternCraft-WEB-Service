from .ropp_service import ROPPService, Result, RailwayService
from .components import CreateTheory


class TheoryService(ROPPService):
    @staticmethod
    def create_theory(raw_json, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "raw_json": raw_json,
                "current_user": current_user,
            },
            steps=(
                (CreateTheory.parse_json, "parse_json"),
                (CreateTheory.validate_authentication, "validate_authentication"),
                (CreateTheory.validate_create_data, "validate_create_data"),
                (CreateTheory.execute, "execute_create"),
                (CreateTheory.format, "format_output"),
            ),
        )
