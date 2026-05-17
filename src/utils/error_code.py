from enum import Enum


class ErrorCode(Enum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503

    @classmethod
    def get_description(cls, code: int) -> str:
        descriptions = {
            cls.BAD_REQUEST: "Bad Request",
            cls.UNAUTHORIZED: "Unauthorized",
            cls.FORBIDDEN: "Forbidden",
            cls.NOT_FOUND: "Not Found",
            cls.INTERNAL_SERVER_ERROR: "Internal Server Error",
            cls.BAD_GATEWAY: "Bad Gateway",
            cls.SERVICE_UNAVAILABLE: "Service Unavailable"
        }

        try:
            return descriptions[cls(code)]
        except ValueError:
            return "Erro desconhecido"
