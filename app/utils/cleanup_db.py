from app import create_app
from app.extensions import db
from app.models import (
    User,
    Problem,
    Solution,
    Comment,
    Like,
    Bookmark,
    ProblemVote,
    DiscourseComment,
    DiscourseReply,
    DiscourseVote,
    DiscourseReplyVote,
)


def cleanup_database():
    """Remove all data from the database."""
    app = create_app()

    with app.app_context():
        print("Starting database cleanup...")

        # Delete all related data first
        print("Deleting discourse data...")
        DiscourseReplyVote.query.delete()
        DiscourseVote.query.delete()
        DiscourseReply.query.delete()
        DiscourseComment.query.delete()

        print("Deleting problem-related data...")
        ProblemVote.query.delete()
        Bookmark.query.delete()
        Like.query.delete()
        Comment.query.delete()

        print("Deleting solutions...")
        Solution.query.delete()

        print("Deleting problems...")
        Problem.query.delete()

        print("Deleting users...")
        User.query.delete()

        # Commit the changes
        db.session.commit()
        print("Database cleanup completed successfully!")


if __name__ == "__main__":
    cleanup_database()
