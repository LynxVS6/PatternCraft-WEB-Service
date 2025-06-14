from .ropp_service import ROPPService, Result, RailwayService
from .components import SubmitVote, TargetBased


class VoteService(ROPPService):
    @staticmethod
    def submit_vote(target_model, vote_model, raw_json, target_id, current_user, vote_class) -> Result:
        return RailwayService.execute_flow(
            {
                "target_model": target_model,
                "vote_model": vote_model,
                "raw_json": raw_json,
                "target_id": target_id,
                "current_user": current_user,
                "vote_class": vote_class
            },
            steps=(
                (SubmitVote.parse_json, "parse_json"),
                (TargetBased.get_target, "get_target"),
                (SubmitVote.validate_vote_class, "validate_vote_class"),
                (SubmitVote.validate_vote_type, "validate_vote_type"),
                (SubmitVote.execute, "execute_submit"),
                (SubmitVote.format, "format_output"),
            )
        )
