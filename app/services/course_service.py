from .ropp_service import ROPPService, Result, RailwayService
from .components import CreateCourse


class CourseService(ROPPService):
    @staticmethod
    def create_course(raw_json, current_user) -> Result:
        """API endpoint for backend filtering (used by AJAX requests)"""
        return RailwayService.execute_flow(
            {
                "raw_json": raw_json,
                "current_user": current_user,
            },
            steps=(
                (CreateCourse.parse_json, "parse_json"),
                (CreateCourse.validate_authentication, "validate_authentication"),
                (CreateCourse.validate_course_data, "validate_course_data"),
                (CreateCourse.execute, "execute_filter"),
                (CreateCourse.format, "format_output"),
            ),
        )
