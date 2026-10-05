from __future__ import annotations

import pytest
from dataclasses import dataclass
from pydantic import ValidationError

from app.routers.chat import ChatRequest, build_messages


@dataclass
class Previous:
    question: str
    answer: str | None
    status: str = "success"


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


def test_history_uses_five_successful_pairs_in_chronological_order():
    recent_first = [Previous(f"질문 {n}", f"답변 {n}") for n in range(6, 0, -1)]
    recent_first.insert(0, Previous("실패한 질문", None, "timeout"))

    messages = build_messages(recent_first, "현재 질문")

    assert len(messages) == 11
    assert messages[0] == {"role": "user", "content": "질문 2"}
    assert messages[-3] == {"role": "user", "content": "질문 6"}
    assert messages[-1] == {"role": "user", "content": "현재 질문"}
    assert "질문 1" not in [message["content"] for message in messages]
