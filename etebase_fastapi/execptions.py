from fastapi import status

from django_etebase.exceptions import EtebaseValidationError


class CustomHttpException(Exception):
    def __init__(self, code: str, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        self.code = code
        self.detail = detail

    @property
    def as_dict(self) -> dict:
        return {"code": self.code, "detail": self.detail}


class AuthenticationFailed(CustomHttpException):
    def __init__(
        self,
        code="authentication_failed",
        detail: str = "Incorrect authentication credentials.",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(code=code, detail=detail, status_code=status_code)


class NotAuthenticated(CustomHttpException):
    def __init__(
        self,
        code="not_authenticated",
        detail: str = "Authentication credentials were not provided.",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(code=code, detail=detail, status_code=status_code)


class PermissionDenied(CustomHttpException):
    def __init__(
        self,
        code="permission_denied",
        detail: str = "You do not have permission to perform this action.",
        status_code: int = status.HTTP_403_FORBIDDEN,
    ):
        super().__init__(code=code, detail=detail, status_code=status_code)


class ValidationError(CustomHttpException):
    def __init__(self, code: str, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(code=code, detail=detail, status_code=status_code)


def flatten_errors(field_name, errors):
    ret = []
    if isinstance(errors, dict):
        for error_key in errors:
            error = errors[error_key]
            ret.extend(flatten_errors("{}.{}".format(field_name, error_key), error))
    else:
        for error in errors:
            if error.messages:
                message = error.messages[0]
            else:
                message = str(error)
            ret.append(
                {
                    "field": field_name,
                    "code": error.code,
                    "detail": message,
                }
            )
    return ret


def transform_validation_error(prefix, err):
    if hasattr(err, "error_dict"):
        errors = flatten_errors(prefix, err.error_dict)
    elif not hasattr(err, "message"):
        errors = flatten_errors(prefix, err.error_list)
    else:
        raise EtebaseValidationError(err.code, err.message)
    raise ValidationError(code="field_errors", detail="Field validations failed.")
    raise serializers.ValidationError(
        {
            "code": "field_errors",
            "detail": "Field validations failed.",
            "errors": errors,
        }
    )
