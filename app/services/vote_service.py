from app.extensions import db
from .base_service import BaseService, Result
from abc import abstractmethod, ABC
from enum import Enum
from typing import Type


class VoteService(BaseService, ABC):
    @classmethod
    @abstractmethod
    def get_vote_type_enum(cls) -> Type[Enum]:
        """Return the enum class for vote types."""
        pass

    @classmethod
    @BaseService._handle_errors
    def submit_vote(cls, target_model, vote_model, raw_data, target_id, current_user) -> Result:
        input_data = {
            "target_model": target_model,
            "vote_model": vote_model,
            "raw_data": raw_data,
            "target_id": target_id,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            cls._parse_input_data,
            BaseService._combine_funcs(
                BaseService._get_target,
                cls._validate_vote_type,
            ),
            cls._handle_vote,
            cls._send_data,
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_input_data(input_data):
        raw_data = input_data["raw_data"]
        vote_type = raw_data["vote_type"]

        return Result(
            True,
            data={
                "target_model": input_data["target_model"],
                "vote_model": input_data["vote_model"],
                "target_id": input_data["target_id"],
                "current_user": input_data["current_user"],
                "vote_type": vote_type,
            },
        )

    @staticmethod
    @BaseService._handle_errors
    def _handle_vote(input_data) -> Result:
        """Generic vote handling function."""
        vote_model = input_data["vote_model"]
        target_id = input_data["target_id"]
        current_user = input_data["current_user"]
        vote_type = input_data["vote_type"]

        existing_vote = vote_model.query.filter_by(
            user_id=current_user.id, target_id=target_id
        ).first()

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                db.session.delete(existing_vote)
                input_data["vote_type"] = None
            else:
                existing_vote.vote_type = vote_type
        else:
            new_vote = vote_model(
                user_id=current_user.id,
                target_id=target_id,
                vote_type=vote_type,
            )
            db.session.add(new_vote)

        db.session.commit()

        return Result(success=True, data=input_data)

    @staticmethod
    @abstractmethod
    def _send_data(input_data) -> Result:
        pass

    @classmethod
    @BaseService._handle_errors
    def _validate_vote_type(cls, input_data) -> Result:
        vote_type = input_data["vote_type"]
        vote_type_enum = cls.get_vote_type_enum()
        allowed_states = [e.value for e in vote_type_enum]

        if vote_type is None:
            return Result(
                success=False,
                error="Vote type is required",
                error_code=400,
            )
        if vote_type not in allowed_states:
            return Result(
                success=False,
                error=f"Invalid vote type. Allowed: {allowed_states}",
                error_code=400,
            )

        return Result(success=True, data=input_data)


class LikeVoteService(VoteService):
    class LikeVoteType(Enum):
        LIKE = "like"
        DISLIKE = "dislike"

    @classmethod
    def get_vote_type_enum(cls) -> Type[Enum]:
        return cls.LikeVoteType

    @staticmethod
    def _send_data(input_data) -> Result:
        target = input_data["target"]
        vote_type = input_data["vote_type"]
        return Result(
            success=True,
            data={
                "likes": target.votes_count,
                "liked": vote_type == LikeVoteService.LikeVoteType.LIKE.value,
            },
        )


class EmojiVoteService(VoteService):
    class EmojiVoteType(Enum):
        POSITIVE = "positive"
        NEUTRAL = "neutral"
        NEGATIVE = "negative"

    @classmethod
    def get_vote_type_enum(cls) -> Type[Enum]:
        return cls.EmojiVoteType

    @staticmethod
    def _send_data(input_data) -> Result:
        target = input_data["target"]
        target.update_vote_counts()
        return Result(
            success=True,
            data={
                "satisfaction_percent": round(target.satisfaction_percent),
                "total_votes": target.total_votes,
                "vote_type": input_data["vote_type"]
            },
        )


class ArrowVoteService(VoteService):
    class ArrowVoteType(Enum):
        UP = "up"
        DOWN = "down"

    @classmethod
    def get_vote_type_enum(cls) -> Type[Enum]:
        return cls.ArrowVoteType

    @staticmethod
    def _send_data(input_data) -> Result:
        target = input_data["target"]
        return Result(success=True, data={"vote_count": target.vote_count})
