from ...ropp_service import Result
from app.extensions import db
from enum import Enum


class EmojiVoteType(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class LikeVoteType(Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class ArrowVoteType(Enum):
    UP = "up"
    DOWN = "down"


class SubmitVote:
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        vote_type = raw_json["vote_type"]

        return Result.ok(
            data={
                "target_model": input_data["target_model"],
                "vote_model": input_data["vote_model"],
                "target_id": input_data["target_id"],
                "current_user": input_data["current_user"],
                "vote_type": vote_type,
                "vote_class": input_data["vote_class"]
            },
        )

    @staticmethod
    def validate_vote_class(input_data) -> Result:
        vote_class = input_data["vote_class"]
        if vote_class == "like":
            input_data.update({"allowed_states": LikeVoteType})
        elif vote_class == "arrow":
            input_data.update({"allowed_states": ArrowVoteType})
        elif vote_class == "emoji":
            input_data.update({"allowed_states": EmojiVoteType})
        else:
            Result.fail(error="Incorrect vote class", error_code=400)
        return Result.ok(input_data)

    @staticmethod
    def validate_vote_type(input_data) -> Result:
        vote_type = input_data["vote_type"]
        allowed_states = input_data["allowed_states"]

        if vote_type is None:
            return Result.fail(
                error="Vote type is required",
                error_code=400,
            )
        if vote_type not in allowed_states:
            return Result.fail(
                error=f"Invalid vote type. Allowed: {allowed_states}",
                error_code=400,
            )

        return Result.ok(input_data)

    @staticmethod
    def execute(input_data) -> Result:
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

        if input_data["vote_class"] == "emoji":
            input_data["target"].update_vote_counts()

        db.session.commit()

        return Result.ok(input_data)

    @staticmethod
    def format(input_data) -> Result:
        vote_class = input_data["vote_class"]
        target = input_data["target"]
        vote_type = input_data["vote_type"]
        if vote_class == "emoji":
            return Result.ok(
                {
                    "satisfaction_percent": round(target.satisfaction_percent),
                    "total_votes": target.total_votes,
                    "vote_type": input_data["vote_type"],
                }
            )
        elif vote_class == "arrow":
            return Result.ok({"vote_count": target.vote_count})
        elif vote_class == "like":
            return Result.ok(
                {
                    "likes": target.votes_count,
                    "liked": vote_type == LikeVoteType.LIKE.value,
                }
            )
        else:
            Result.fail(error="Incorrect vote class", error_code=400)
        return Result.ok(input_data)
