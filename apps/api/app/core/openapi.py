from __future__ import annotations
from app.schemas.errors import ErrorResponse

COMMON_ERROR_RESPONSES: dict[int, dict[str, type[ErrorResponse]]] = {
    400: {"model": ErrorResponse, 
          "description": "Bad Request", 
          "content": {
            "application/json": {
                "example": {
                    "code":"user.not_found",
                    "detail":"The requested user does not exist.",
                    "meta": None
                    },
                }
            },
        },
    401: {"model": ErrorResponse, 
          "description": "Unauthorized",
          "content": {
            "application/json": {
                "example": {
                    "code":"unauthorized",
                    "detail":"Authentication is required and has failed or has not yet been provided.",
                    "meta": None
                    },
                }
            },
        },
    403: {"model": ErrorResponse, 
          "description": "Forbidden",
          "content": {
            "application/json": {
                "example": {
                    "code":"forbidden",
                    "detail":"You do not have permission to access this resource.",
                    "meta": None
                    },
                }
            },
        },
    404: {"model": ErrorResponse, 
          "description": "Not Found",
          "content": {
            "application/json": {
                "example": {
                    "code":"user.not_found",
                    "detail":"The requested user does not exist.",
                    "meta": None
                    },
                }
            },
        },
    409: {"model": ErrorResponse, 
          "description": "Conflict",
          "content": {
            "application/json": {
                "example": {
                    "code":"user.username_already_exists",
                    "detail":"The username is already taken.",
                    "meta": None
                    },
            }
          }
        },
    422: {"model": ErrorResponse,
          "description": "Unprocessable Entity",
          "content": {
            "application/json": {
                "example": {
                    "code":"validation_error",
                    "detail":"Request validation failed.",
                    "meta": None
                    },
                }
            },
        },
    500: {"model": ErrorResponse,
          "description": "Internal Server Error",
          "content": {
            "application/json": {
                "example": {
                    "code":"internal_server_error",
                    "detail":"An internal server error occurred.",
                    "meta": None
                    },
                }
            },
        },
}