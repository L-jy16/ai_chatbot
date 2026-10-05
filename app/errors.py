from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

DEFAULT_INVALID_INPUT_MESSAGE = "입력값이 올바르지 않아요."


class APIError(Exception):
    """{"error": 코드, "message": 안내 문구} 형식으로 응답할 예외."""

    def __init__(self, status_code: int, error: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error = error
        self.message = message


async def handle_api_error(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "message": exc.message},
    )


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """요청 검증 실패를 422 INVALID_INPUT으로 바꾼다.

    Pydantic validator가 던진 ValueError의 문구가 있으면 그대로 쓰고,
    없으면(필드 누락, 타입 오류, 깨진 JSON) 기본 문구를 쓴다.
    """
    message = DEFAULT_INVALID_INPUT_MESSAGE
    for err in exc.errors():
        cause = (err.get("ctx") or {}).get("error")
        if isinstance(cause, ValueError):
            message = str(cause)
            break
    return JSONResponse(status_code=422, content={"error": "INVALID_INPUT", "message": message})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIError, handle_api_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
