from fastapi import FastAPI, Request, Response
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

DEFAULT_INVALID_INPUT_MESSAGE = "입력값이 올바르지 않아요."
# FastAPI가 요청 본문을 읽지 못했을 때(잘못된 UTF-8, 너무 큰 정수, 지나친 중첩 등) 던지는 400의 detail
BODY_PARSE_ERROR_DETAIL = "There was an error parsing the body"


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


async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> Response:
    """본문 파싱 실패(400)만 INVALID_INPUT 형식으로 바꾸고, 나머지(404 등)는 FastAPI 기본 처리에 맡긴다."""
    if exc.status_code == 400 and exc.detail == BODY_PARSE_ERROR_DETAIL:
        return JSONResponse(
            status_code=422,
            content={"error": "INVALID_INPUT", "message": DEFAULT_INVALID_INPUT_MESSAGE},
        )
    return await http_exception_handler(request, exc)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIError, handle_api_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
