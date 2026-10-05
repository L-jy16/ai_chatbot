"""실제 API를 한 번 호출하여 가입→로그인→Q4→기록 조회 검증 (임시 DB 사용).
프로젝트 루트에서 .venv/bin/python -m scripts.check_connection 으로 실행.
실제 키/비밀번호/AI 답변은 출력하지 않는다. API 사용량이 발생할 수 있다.
"""
import os
import secrets
import tempfile
from pathlib import Path


def main():
    with tempfile.TemporaryDirectory(prefix='shorts-smoke-') as temp:
        os.environ['DATABASE_URL'] = f'sqlite:///{Path(temp) / "check.db"}'
        from fastapi.testclient import TestClient
        from app.config import settings
        from app.main import app
        print('AI model:', settings.LLM_MODEL)
        print('Naver configured:', bool(settings.NAVER_CLIENT_ID and settings.NAVER_CLIENT_SECRET))
        with TestClient(app) as client:
            credentials={'email':'connection-test@example.com','password':secrets.token_urlsafe(20)}
            assert client.post('/api/auth/signup',json=credentials).status_code==201
            assert client.post('/api/auth/login',json=credentials).status_code==200
            result=client.post('/api/chat',json={
                'mode':'q4','message':'금리 인하를 쉽게 설명하는 숏폼을 기획해 줘. 자료가 없으면 그 한계를 알려줘.',
                'keyword':'금리 인하',
            })
            print('Chat HTTP:',result.status_code)
            if result.status_code!=200:
                print('Error code:',result.json().get('error'))
                raise SystemExit(1)
            print('Answer characters:',len(result.json()['answer']))
            history=client.get('/api/me/chats').json()
            assert len(history)==1 and history[0]['status']=='success'
            assert history[0]['answer']==result.json()['answer']
            print('Signup / login / live AI / history: PASS')


if __name__=='__main__':
    main()
