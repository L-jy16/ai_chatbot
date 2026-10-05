import asyncio

import httpx2 as httpx
import pytest

from app.config import settings
from app.services import llm


@pytest.fixture
def transport(monkeypatch):
    monkeypatch.setattr(settings,'LLM_API_KEY','unit-test-secret')
    monkeypatch.setattr(settings,'LLM_MODEL','unit-model')
    monkeypatch.setattr(settings,'LLM_BASE_URL','https://example.test/v1')
    factory=httpx.AsyncClient
    def install(handler):
        monkeypatch.setattr(llm.httpx,'AsyncClient',lambda **kw:factory(transport=httpx.MockTransport(handler),**kw))
    return install


def test_llm_request_and_response(transport):
    import json
    def handler(request):
        assert str(request.url)=='https://example.test/v1/chat/completions'
        assert request.headers['authorization']=='Bearer unit-test-secret'
        body=json.loads(request.content)
        assert body['model']=='unit-model'
        assert body['messages']==[{'role':'system','content':'instructions'},{'role':'user','content':'hello'}]
        return httpx.Response(200,json={'choices':[{'message':{'content':'안녕하세요'}}]})
    transport(handler)
    assert asyncio.run(llm.ask_llm('instructions',[{'role':'user','content':'hello'}]))=='안녕하세요'


@pytest.mark.parametrize('status,body',[(401,{'error':'unit-test-secret'}),(200,{}),(200,{'choices':[{'message':{'content':None}}]})])
def test_llm_error_is_safe(transport,status,body,caplog):
    transport(lambda req:httpx.Response(status,json=body))
    with pytest.raises(llm.AIError):asyncio.run(llm.ask_llm('system',[]))
    assert 'unit-test-secret' not in caplog.text


def test_llm_timeout(transport):
    def handler(req):raise httpx.ReadTimeout('timed out',request=req)
    transport(handler)
    with pytest.raises(llm.AITimeoutError):asyncio.run(llm.ask_llm('system',[]))
