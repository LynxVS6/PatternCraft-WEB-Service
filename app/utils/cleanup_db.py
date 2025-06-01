from app import create_app, db
from app.models import (
    User,
    Problem,
    Solution,
    Comment,
    Like,
    Bookmark,
    ProblemVote,
    DiscourseComment,
    DiscourseVote,
    CommentVote,
)
from sqlalchemy import text


def cleanup_database():
    """Remove all data from the database."""
    app = create_app()

    with app.app_context():
        print("Starting database cleanup...")

        # Disable foreign key checks temporarily
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        # Delete data from all tables in reverse order of dependencies
        tables = [
            CommentVote,
            Comment,
            Like,
            Solution,
            DiscourseVote,
            DiscourseComment,
            ProblemVote,
            Bookmark,
            Problem,
            User,
        ]

        for table in tables:
            db.session.execute(text(f"TRUNCATE TABLE {table.__tablename__}"))
            # Reset auto-increment to 1
            db.session.execute(
                text(f"ALTER TABLE {table.__tablename__} AUTO_INCREMENT = 1")
            )
            print(f"Cleaned {table.__tablename__}")

        # Re-enable foreign key checks
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

        # Commit the changes
        db.session.commit()
        print("Database cleanup completed successfully!")


if __name__ == "__main__":
    cleanup_database()
