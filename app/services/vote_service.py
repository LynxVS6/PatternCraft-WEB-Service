from app.extensions import db
from .base_service import BaseService, Result
from abc import ABC, abstractmethod


class VoteService(BaseService):
    @staticmethod
    @BaseService.handle_errors
    def _handle_vote_type(target_model, vote_model, user_id, target_id, vote_type) -> Result:
        """Generic vote handling function."""
        target = target_model.query.get(target_id)
        if not target:
            return Result(
                success=False,
                error=f"Target model with id {target_id} not found",
                error_code=400,
            )

        existing_vote = vote_model.query.filter_by(
            user_id=user_id, target_id=target_id
        ).first()

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                db.session.delete(existing_vote)
                vote_type = None
            else:
                existing_vote.vote_type = vote_type
        else:
            new_vote = vote_model(
                user_id=user_id, target_id=target_id, vote_type=vote_type
            )
            db.session.add(new_vote)

        db.session.commit()

        return Result(
            success=True,
            data={
                "vote_type": vote_type,
                "action": (
                    "deleted"
                    if existing_vote and existing_vote.vote_type == vote_type
                    else "updated"
                ),
                "target": target
            },
        )

    @staticmethod
    @abstractmethod
    def submit_vote(target_model, vote_model, user_id, target_id, vote_type) -> Result:
        pass


class LikeVoteService(VoteService):
    @staticmethod
    def submit_vote(solution, solution_vote, user_id, target_id, vote_type) -> Result:
        result = VoteService._handle_vote_type(
            solution, solution_vote, user_id, target_id, vote_type
        )

        if result.success and result.data:
            target = result.data["target"]
            result.data.update({
                "likes": target.votes_count,
                "liked": result.data["vote_type"] == "like"
            })

        return result


class EmojiVoteService(VoteService):
    @staticmethod
    def submit_vote(problem, problem_vote, user_id, target_id, vote_type) -> Result:
        result = VoteService._handle_vote_type(
            problem, problem_vote, user_id, target_id, vote_type
        )

        if result.success and result.data:
            target = result.data["target"]
            target.update_vote_counts()
            # No need to refresh since we're using the same object
            # and update_vote_counts() already updated the database

            result.data.update({
                "satisfaction_percent": round(target.satisfaction_percent),
                "total_votes": target.total_votes
            })

        return result


class ArrowVoteService(VoteService):
    @staticmethod
    def submit_vote(comment, comment_vote, user_id, target_id, vote_type) -> Result:
        result = VoteService._handle_vote_type(
            comment, comment_vote, user_id, target_id, vote_type
        )

        if result.success and result.data:
            target = result.data["target"]
            result.data.update({
                "vote_count": target.vote_count
            })

        return result
