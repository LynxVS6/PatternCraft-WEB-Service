from .ropp_service import ROPPService, Result, RailwayService
from .components import TargetBased, SubmitDescription, CheckAuth


class DescriptionService(ROPPService):
    @staticmethod
    def submit_description(target_model, raw_json, target_id, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "target_model": target_model,
                "raw_json": raw_json,
                "target_id": target_id,
                "current_user": current_user,
            },
            steps=(
                (SubmitDescription.parse_json, "parse_json"),
                (TargetBased.get_target, "get_target"),
                (SubmitDescription.validate_author, "validate_author"),
                (
                    SubmitDescription.validate_description_data,
                    "validate_description_data",
                ),
                (SubmitDescription.execute, "execute_submit"),
                (SubmitDescription.format, "format_output"),
            ),
        )

    @staticmethod
    def check_edit_auth(target_model, target_id, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "target_model": target_model,
                "target_id": target_id,
                "current_user": current_user,
            },
            steps=(
                (CheckAuth.validate_author, "validate_author"),
                (CheckAuth.format, "format_output"),
            ),
        )
