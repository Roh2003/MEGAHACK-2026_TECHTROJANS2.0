"""
Generic response formatter — use anywhere across all services.

Usage:
    from shared.response import success, error, paginated

    return success(data={"user": ...}, message="Registered successfully", code=201)
    return error(message="Not found", code=404)
    return paginated(data=[...], total=100, page=1, limit=10)
"""

from typing import Any, Optional
from fastapi.responses import JSONResponse


def success(
    data: Any = None,
    message: str = "Success",
    code: int = 200,
) -> JSONResponse:
    """
    Return a successful JSON response.

    Args:
        data:    The payload to return (dict, list, str, etc.)
        message: Human-readable success message.
        code:    HTTP status code. Default 200.
    """
    return JSONResponse(
        status_code=code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
    )


def error(
    message: str = "An error occurred",
    code: int = 400,
    details: Optional[Any] = None,
) -> JSONResponse:
    """
    Return an error JSON response.

    Args:
        message: Human-readable error message.
        code:    HTTP status code. Default 400.
        details: Optional extra info (validation errors, field names, etc.)
    """
    body: dict = {
        "success": False,
        "message": message,
    }
    if details is not None:
        body["details"] = details

    return JSONResponse(status_code=code, content=body)


def paginated(
    data: list,
    total: int,
    page: int,
    limit: int,
    message: str = "Success",
    code: int = 200,
) -> JSONResponse:
    """
    Return a paginated list response.

    Args:
        data:    List of items for the current page.
        total:   Total number of items across all pages.
        page:    Current page number (1-based).
        limit:   Number of items per page.
        message: Human-readable message.
        code:    HTTP status code. Default 200.
    """
    return JSONResponse(
        status_code=code,
        content={
            "success": True,
            "message": message,
            "data": data,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
            },
        },
    )
