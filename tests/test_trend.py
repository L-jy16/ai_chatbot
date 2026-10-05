import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest
import requests

from app.config import settings
from app.services import trend
from app.services.scenarios import q1, q3


def points(past, recent):
    end=datetime.now(ZoneInfo('Asia/Seoul')).date()-timedelta(days=1)
    return [{'period':(end-timedelta(days=13-i)).isoformat(),'ratio':past if i<7 else recent} for i in range(14)]


@pytest.mark.parametrize('past,recent,expected',[(30,60,'rising'),(60,30,'falling'),(90,90,'peak'),(30,30,'stable')])
def test_comparison(past,recent,expected,monkeypatch):
    monkeypatch.setattr(trend,'_request_datalab',lambda *args: points(past,recent))
    result=trend.compare_periods('금리')
    assert result['trend']==expected and result['available'] is True
    assert result['recent']==recent and result['past']==past


@pytest.mark.parametrize('data',[[],points(0,0),points(30,60)[:7],[{'period':'invalid','ratio':'bad'}]])
def test_missing_data_is_unknown(monkeypatch,data):
    monkeypatch.setattr(trend,'_request_datalab',lambda *args:data)
    result=trend.compare_periods('금리')
    assert result['trend']=='unknown' and result['recent'] is None


def test_client_reads_shared_settings_and_cleans_news(monkeypatch):
    monkeypatch.setattr(settings,'NAVER_CLIENT_ID','test-id')
    monkeypatch.setattr(settings,'NAVER_CLIENT_SECRET','test-secret')
    response=Mock()
    response.json.return_value={'items':[{'title':'<b>금리</b> &amp; 환율','link':'https://example.com'}]}
    get=Mock(return_value=response)
    monkeypatch.setattr(trend.requests,'get',get)
    assert trend.search_news()[0]['title']=='금리 & 환율'
    assert get.call_args.kwargs['headers']['X-Naver-Client-Id']=='test-id'
    assert get.call_args.kwargs['timeout']>0


def test_naver_failure_does_not_log_secrets(monkeypatch,caplog):
    monkeypatch.setattr(settings,'NAVER_CLIENT_ID','test-id')
    monkeypatch.setattr(settings,'NAVER_CLIENT_SECRET','do-not-log-this')
    monkeypatch.setattr(trend.requests,'get',Mock(side_effect=requests.Timeout('do-not-log-this')))
    assert trend.search_news()==[]
    assert 'do-not-log-this' not in caplog.text


def test_q1_includes_comparison_and_channel_context(monkeypatch):
    monkeypatch.setattr(trend,'get_hot_issues',lambda *args:[{'title':'금리 뉴스','link':'https://example.com','pub_date':'today'}])
    monkeypatch.setattr(trend,'compare_periods',lambda k:{'recent':60,'past':30,'trend':'rising','available':True})
    result=asyncio.run(q1.build_prompt('오늘 주제'))
    assert '"recent": 60' in result and '과거 업로드' in result


def test_q3_extracts_keyword_and_includes_unknown(monkeypatch):
    compare=Mock(return_value={'recent':None,'past':None,'trend':'unknown','available':False})
    monkeypatch.setattr(trend,'compare_periods',compare)
    monkeypatch.setattr(trend,'search_news',lambda *args:[])
    result=asyncio.run(q3.build_prompt('금리 인하 주제 지금 올려도 돼?'))
    compare.assert_called_once_with('금리 인하')
    assert '"available": false' in result and '판단 보류' in result
