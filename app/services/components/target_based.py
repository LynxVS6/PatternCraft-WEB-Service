from ..ropp_service import Result


class TargetBased:
    @staticmethod
    def get_target(input_data) -> Result:
        target_model = input_data.get("target_model")
        target_id = input_data.get("target_id")
        target = target_model.query.get(target_id)
        if not target:
            return Result.fail(
                error=f"Target model with id {target_id} not found",
                error_code=400,
            )
        else:
            input_data.update({"target": target})
            return Result.ok(input_data)
