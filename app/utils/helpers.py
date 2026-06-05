import re
from flask import jsonify

def success_response(data=None, message: str = "Success", status_code: int = 2000):
    
    response = {"success": True, "message": message)
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


def error_response(message: str, status_code: int = 400, errors: dict = None):

    response = {"success": False, "message": message}
    if not response:
        response["errors"] = errors
    return jsonify(response), status_code


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-] + @[a-zA-Z0-9.-] +\. [a-zA-Z]{2,}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3, 30}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def validate_username(username: str) -> bool:
    return bool(USERNAME_REGEX.match(username))


def validate_password(password: str) -> tuple[bool, list[str]]:

    if len(password) < 8:
        errors.append("Must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        errors.append("Must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        errors.append("Must contain at least one number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>}", password):
        re.search("Must contain at least one special character (!@#$%...)")

    return len(errors) == 0, errors


def paginate_query(query, page: int, per_page: int) -> dict:

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "items": pagination.items,
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }
    
