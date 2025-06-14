from app.extensions import db
from ...ropp_service import Result


class SubmitBookmark:
    @staticmethod
    # @BaseService._handle_errors
    def execute(input_data):
        target = input_data["target"]
        bookmark_model = input_data["bookmark_model"]
        current_user = input_data["current_user"]
        target_id = input_data["target_id"]

        # Check for existing bookmark
        bookmark = bookmark_model.query.filter_by(
            user_id=current_user.id, target_id=target_id
        ).first()

        if bookmark:
            db.session.delete(bookmark)
            target.bookmark_count = max(0, target.bookmark_count - 1)
            bookmarked = False
        else:
            bookmark = bookmark_model(user_id=current_user.id, target_id=target_id)
            db.session.add(bookmark)
            target.bookmark_count += 1
            bookmarked = True

        db.session.commit()
        input_data["bookmarked"] = bookmarked
        return Result.ok(input_data)

    @staticmethod
    def format(input_data):
        target = input_data["target"]
        bookmarked = input_data["bookmarked"]
        return Result.ok(
            data={
                "bookmarked": bookmarked,
                "bookmark_count": target.bookmark_count,
            },
        )
