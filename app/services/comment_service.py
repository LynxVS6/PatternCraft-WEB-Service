from .ropp_service import ROPPService, Result, RailwayService
from .components import SubmitComment, EditComment, DeleteComment, TargetBased


class CommentService(ROPPService):
    @staticmethod
    def submit_comment(
        target_model, comment_model, raw_json, target_id, current_user
    ) -> Result:
        return RailwayService.execute_flow(
            {
                "target_model": target_model,
                "comment_model": comment_model,
                "raw_json": raw_json,
                "target_id": target_id,
                "current_user": current_user,
            },
            steps=(
                (SubmitComment.parse_json, "parse_json"),
                (TargetBased.get_target, "get_target"),
                (SubmitComment.validate_comment_data, "validate_comment_data"),
                (SubmitComment.execute, "execute_submit"),
                (SubmitComment.format, "format_output"),
            ),
        )

    @staticmethod
    def edit_comment(comment_model, raw_json, comment_id, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "comment_model": comment_model,
                "raw_json": raw_json,
                "comment_id": comment_id,
                "current_user": current_user,
            },
            steps=(
                (EditComment.parse_json, "parse_json"),
                (EditComment.get_comment, "get_comment"),
                (EditComment.validate_author, "validate_author"),
                (EditComment.validate_comment_data, "validate_comment_data"),
                (EditComment.execute, "execute_edit"),
                (EditComment.format, "format_output"),
            ),
        )

    @staticmethod
    def delete_comment(comment_model, comment_id, current_user):
        return RailwayService.execute_flow(
            {
                "comment_model": comment_model,
                "comment_id": comment_id,
                "current_user": current_user,
            },
            steps=(
                (DeleteComment.get_comment, "get_comment"),
                (DeleteComment.validate_author, "validate_author"),
                (DeleteComment.execute, "execute_edit"),
                (DeleteComment.format, "format_output"),
            ),
        )
