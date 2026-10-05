import pytest
from pydantic import ValidationError

from app.routers.chat import ChatRequest


@pytest.mark.parametrize("message", ["", "  ", "x" * 501, 42, None])
def test_chat_rejects_invalid_question_before_provider_call(message):
    with pytest.raises(ValidationError):
        ChatRequest(mode="q5", message=message)


def test_chat_trims_question_before_length_check():
    request = ChatRequest(mode="q5", message="  오늘 주제  ")
    assert request.message == "오늘 주제"


@pytest.mark.parametrize("mode", ["q2", "Q5", "", 42])
def test_chat_rejects_unowned_or_unknown_mode(mode):
    with pytest.raises(ValidationError):
        ChatRequest(mode=mode, message="질문")
