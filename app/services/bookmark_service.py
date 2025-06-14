from .ropp_service import ROPPService, Result, RailwayService
from .components import SubmitBookmark, TargetBased


class BookmarkService(ROPPService):
    @staticmethod
    def submit_bookmark(
        target_model, bookmark_model, target_id, current_user
    ) -> Result:
        return RailwayService.execute_flow(
            {
                "target_model": target_model,
                "bookmark_model": bookmark_model,
                "target_id": target_id,
                "current_user": current_user,
            },
            steps=(
                (TargetBased.get_target, "get_target"),
                (SubmitBookmark.execute, "execute_submit"),
                (SubmitBookmark.format, "format_output"),
            ),
        )
