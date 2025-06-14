from .ropp_service import ROPPService, Result, RailwayService

from .components import ChangePassword, EditProfile


class UserService(ROPPService):
    @staticmethod
    def edit_profile(raw_json, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "raw_json": raw_json,
                "current_user": current_user,
            },
            steps=(
                (EditProfile.parse_json, "parse_json"),
                (EditProfile.validate_authentication, "validate_authentication"),
                (EditProfile.validate_user_data, "validate_user_data"),
                (EditProfile.execute, "execute_edit"),
                (EditProfile.format, "format_output"),
            ),
        )

    @staticmethod
    def change_password(raw_json, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "raw_json": raw_json,
                "current_user": current_user,
            },
            steps=(
                (ChangePassword.parse_json, "parse_json"),
                (ChangePassword.validate_authentication, "validate_authentication"),
                (ChangePassword.validate_password_change, "validate_password_change"),
                (ChangePassword.execute, "execute_change"),
                (ChangePassword.format, "format_output"),
            ),
        )
