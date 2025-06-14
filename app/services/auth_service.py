from .ropp_service import ROPPService, Result, RailwayService
from .components import ConfirmEmail, LoginUser, RegisterUser


class AuthService(ROPPService):
    @staticmethod
    def register(raw_json, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "raw_json": raw_json,
                "current_user": current_user,
            },
            steps=(
                (RegisterUser.parse_json, "parse_json"),
                (RegisterUser.validate_user_data, "validate_register_data"),
                (RegisterUser.execute, "execute_register"),
                (RegisterUser.format, "format_output"),
            ),
        )

    @staticmethod
    def login(raw_json, current_user) -> Result:
        return RailwayService.execute_flow(
            {
                "raw_json": raw_json,
                "current_user": current_user,
            },
            steps=(
                (LoginUser.parse_json, "parse_json"),
                (LoginUser.validate_credentials, "validate_credentials"),
                (LoginUser.execute, "execute_login"),
                (LoginUser.format, "format_output"),
            ),
        )

    @staticmethod
    def confirm_email(token) -> Result:
        return RailwayService.execute_flow(
            {"token": token},
            steps=(
                (ConfirmEmail.validate_token, "validate_token"),
                (ConfirmEmail.validate_user, "validate_user"),
                (ConfirmEmail.execute, "execute_confirmation"),
                (ConfirmEmail.format, "format_output"),
            ),
        )
