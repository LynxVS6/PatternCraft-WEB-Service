from .ropp_service import ROPPService, Result, RailwayService
from .components import CreateProblem, FilterProblemsAPI, FilterProblemsFrontend


class ProblemService(ROPPService):
    @staticmethod
    def filter_problems_api(raw_json, current_user) -> Result:
        """API endpoint for backend filtering (used by AJAX requests)"""
        return RailwayService.execute_flow(
            {
                "raw_json": raw_json,
                "current_user": current_user,
            },
            steps=(
                (FilterProblemsAPI.parse_json, "parse_json"),
                (FilterProblemsAPI.validate_authentication, "validate_authentication"),
                (FilterProblemsAPI.validate_filter_data, "validate_authentication"),
                (FilterProblemsAPI.execute, "execute_filter"),
                (FilterProblemsAPI.format, "format_output"),
            ),
        )

    @staticmethod
    def filter_problems_frontend(
        search_query,
        order_by,
        language,
        status,
        progress,
        difficulties,
        selected_tags,
        page,
        per_page,
        current_user,
    ) -> Result:
        """Frontend filtering for problem hub page"""
        return RailwayService.execute_flow(
            {
                "search_query": search_query,
                "order_by": order_by,
                "language": language,
                "status": status,
                "progress": progress,
                "difficulties": difficulties,
                "selected_tags": selected_tags,
                "page": page,
                "per_page": per_page,
                "current_user": current_user,
            },
            steps=(
                (
                    FilterProblemsFrontend.validate_authentication,
                    "validate_authentication",
                ),
                (FilterProblemsFrontend.execute, "execute_filter"),
                (FilterProblemsFrontend.format, "format_output"),
            ),
        )

    @staticmethod
    def create_problem(raw_json, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "raw_json": raw_json,
                "current_user": current_user,
            },
            steps=(
                (CreateProblem.parse_json, "parse_json"),
                (CreateProblem.validate_authentication, "validate_authentication"),
                (CreateProblem.validate_create_data, "validate_create_data"),
                (CreateProblem.execute, "execute_create"),
                (CreateProblem.format, "format_output"),
            ),
        )
