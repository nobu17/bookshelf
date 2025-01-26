class ApiException(Exception):
    status_code: int = 400
    detail: str = "API error"


class DataNotFoundError(Exception):
    notfound_id: str
    entity: str
    detail: str

    def __init__(self, notfound_id: str, entity: str, detail: str, *args, **kwargs):
        self.notfound_id = notfound_id
        self.entity = entity
        self.detail = detail

        msg = f"DataNotFound。Entity:{entity}, ID:{notfound_id} Details:{detail}"

        super().__init__(msg, *args, **kwargs)


class DuplicateItemError(Exception):
    entity: str
    param_name: str
    param_value: str

    def __init__(self, entity: str, param_name: str, param_value: str, *args, **kwargs):
        self.entity = entity
        self.param_name = param_name
        self.param_value = param_value

        msg = f"Duplicate Item exists. entity:{entity}, name:{param_name}, value:{param_value}"

        super().__init__(msg, *args, **kwargs)


class AppValidationError(Exception):
    name: str
    detail: str

    def __init__(self, name: str, detail: str, *args, **kwargs):
        self.name = name
        self.detail = detail

        msg = f"Input validation error. Name:{name}, Details:{detail}"

        super().__init__(msg, *args, **kwargs)


class DomainValidationError(Exception):
    name: str
    detail: str

    def __init__(self, name: str, detail: str, *args, **kwargs):
        self.name = name
        self.detail = detail

        msg = f"Input validation error. Name:{name}, Details:{detail}"

        super().__init__(msg, *args, **kwargs)


class AuthFailedError(Exception):
    detail: str  # for internal usage. should not output

    def __init__(self, detail: str, *args, **kwargs):
        self.detail = detail
        msg = "Failed to auth. may wrong email or password"

        super().__init__(msg, *args, **kwargs)


class AuthCredentialsError(Exception):
    detail: str  # for internal usage. should not output

    def __init__(self, detail: str, *args, **kwargs):
        self.detail = detail
        msg = "Incorrect credentials or expired"

        super().__init__(msg, *args, **kwargs)


class InvalidAuthError(Exception):
    detail: str  # for internal usage. should not output

    def __init__(self, detail: str, *args, **kwargs):
        self.detail = detail
        msg = "Invalid authorization information."

        super().__init__(msg, *args, **kwargs)


class AuthRolePermissionError(Exception):
    required_role: str  # for internal usage. should not output

    def __init__(self, required_role: str, *args, **kwargs):
        self.required_role = required_role
        msg = f"Role permission is denied. {required_role} role is needed."

        super().__init__(msg, *args, **kwargs)
