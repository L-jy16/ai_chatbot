# ai_chatbot

경제 숏폼 트렌드 챗봇 (FastAPI)

## 실행 방법

요구 사항: Python 3.10 이상

```bash
# 1. 가상환경 만들기
python3 -m venv .venv
source .venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 파일 만들기
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # 출력값을 .env의 SECRET_KEY에 붙여넣기

# 4. 서버 실행 (첫 실행 때 app.db와 테이블이 자동으로 생성됨)
uvicorn app.main:app --reload

# 5. 동작 확인
curl http://127.0.0.1:8000/health   # {"status":"ok"}
```

- API 문서(Swagger): http://127.0.0.1:8000/docs
- 외부에서 접속해야 할 때(배포)는 `uvicorn app.main:app --host 0.0.0.0 --port 8000`으로 실행한다.

## 테스트

```bash
pytest
```

테스트는 매번 임시 SQLite 파일을 만들어 쓰므로 `app.db`를 건드리지 않는다.

## 환경 변수

`.env.example`을 `.env`로 복사해서 값을 채운다. `.env`는 `.gitignore`에 들어 있어 커밋되지 않는다. 새 키가 생기면 `.env.example`에 이름과 설명만 추가한다.

| 변수 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `SECRET_KEY` | O | 없음 | 세션 쿠키 서명 키. 16자 이상. 비어 있으면 서버가 시작되지 않는다 |
| `DATABASE_URL` | X | `sqlite:///./app.db` | DB 연결 주소 |
| `NAVER_CLIENT_ID` | X | 빈 값 | 네이버 API 클라이언트 ID |
| `NAVER_CLIENT_SECRET` | X | 빈 값 | 네이버 API 클라이언트 시크릿 |
| `LLM_API_KEY` | X | 빈 값 | LLM API 키 (서버에서만 사용) |
| `LLM_MODEL` | X | 빈 값 | 사용할 LLM 모델 이름 |
| `LLM_TIMEOUT_SECONDS` | X | `30` | LLM 호출 타임아웃(초) |
