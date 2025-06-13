from app.extensions import db
from .base_service import BaseService, Result


class DescriptionService(BaseService):
    @staticmethod
    def submit_description(target_model, raw_data, target_id, current_user) -> Result:
        input_data = {
            "target_model": target_model,
            "raw_data": raw_data,
            "target_id": target_id,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            DescriptionService._parse_input_data,
            BaseService._combine_funcs(
                BaseService._get_target,
                DescriptionService._validate_author,
                DescriptionService._validate_description_data,
            ),
            DescriptionService._handle_submit,
            DescriptionService._send_data,
        )

    @staticmethod
    def check_edit_auth(target_model, target_id, current_user) -> Result:
        input_data = {
            "target_model": target_model,
            "target_id": target_id,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            DescriptionService._parse_auth_check,
            BaseService._combine_funcs(
                BaseService._get_target,
                DescriptionService._validate_author,
            ),
            DescriptionService._handle_auth_check,
            DescriptionService._send_auth_data,
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_input_data(input_data):
        raw_data = input_data["raw_data"]
        description = raw_data.get("description")
        input_data["description"] = description
        return Result(True, data=input_data)

    @staticmethod
    @BaseService._parse_errors
    def _parse_auth_check(input_data):
        return Result(True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_submit(input_data):
        target = input_data["target"]
        description = input_data["description"]
        target.description = description
        db.session.commit()
        return Result(True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_auth_check(input_data):
        return Result(True, data=input_data)

    @staticmethod
    def _validate_author(input_data):
        target = input_data["target"]
        current_user = input_data["current_user"]
        if target.author_id != current_user.id:
            return Result(
                success=False,
                error="Only the author can update the description",
                error_code=403,
            )
        return Result(True, data=input_data)

    @staticmethod
    def _validate_description_data(input_data) -> Result:
        description = input_data["description"]
        if description is None:
            return Result(
                success=False,
                error="Description is required",
                error_code=400,
            )
        if not isinstance(description, str):
            return Result(
                success=False,
                error="Description must be a string",
                error_code=400,
            )
        if not (1 <= len(description) <= 5000):
            return Result(
                success=False,
                error="Description must be between 1 and 5000 characters",
                error_code=400,
            )
        return Result(success=True, data=input_data)

    @staticmethod
    def _send_data(input_data):
        target_id = input_data["target_id"]
        description = input_data["description"]
        return Result(
            success=True,
            data={
                "target_id": target_id,
                "description": description,
            },
        )

    @staticmethod
    def _send_auth_data(input_data):
        return Result(
            success=True,
            data={"message": "Authorized to edit description"},
        )
