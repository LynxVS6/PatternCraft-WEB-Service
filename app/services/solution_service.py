from .ropp_service import ROPPService, Result, RailwayService
from .components import SubmitSolution, TargetBased


class SolutionService(ROPPService):
    @staticmethod
    def submit_solution(target_model, target_id, raw_json, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "target_model": target_model,
                "target_id": target_id,
                "raw_json": raw_json,
                "current_user": current_user
            },
            steps=(
                (SubmitSolution.parse_json, "parse_json"),
                (TargetBased.get_target, "get_target"),
                (SubmitSolution.validate_authentication, "validate_authentication"),
                (SubmitSolution.validate_solution_data, "validate_solution_data"),
                (SubmitSolution.execute, "execute_submit"),
                (SubmitSolution.format, "format_output"),
            ),
        )
