from app.extensions import db
from .base_service import BaseService, Result


class BookmarkService(BaseService):
    @staticmethod
    def submit_bookmark(target_model, bookmark_model, target_id, current_user) -> Result:
        return BaseService._process_input_data(
            {
                "target_model": target_model,
                "bookmark_model": bookmark_model,
                "target_id": target_id,
                "current_user": current_user,
            },
            BookmarkService._parse_input_data,
            BaseService._get_target,
            BookmarkService._handle_submit,
            BookmarkService._send_data,
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_input_data(input_data):
        return Result(True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_submit(input_data):
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
        return Result(True, data=input_data)


    @staticmethod
    def _send_data(input_data):
        target = input_data["target"]
        bookmarked = input_data["bookmarked"]
        return Result(
            success=True,
            data={
                "bookmarked": bookmarked,
                "bookmark_count": target.bookmark_count,
            },
        )
