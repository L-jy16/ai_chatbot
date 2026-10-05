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

## A·B 연결 및 AI 채팅

브라우저에서 `http://127.0.0.1:8000`에 접속해 **회원가입 → 로그인 → Q1 또는 Q4 선택 → 질문** 순서로 사용한다.

- Q1: 최신 경제 뉴스에 등장하는 경제 키워드 최대 3개를 골라 최근/이전 7일 추이를 함께 전달한다. 이전 업로드 주제는 질문이나 이전 대화로 받는다.
- Q4: 분석 키워드를 직접 지정할 수 있다. 생략하면 질문에서 요청 표현을 제거해 추출한다. 추출이 부정확하면 키워드 칸에 정확히 입력한다.
- 로그인한 사용자의 최근 성공 대화 5개를 AI에 전달한다. 성공·시간 초과·오류 기록은 사용자별로 저장한다.
- **내 대화 기록**에서 현재 로그인한 사용자의 기록만 볼 수 있다.
- 현재 화면과 API에서 지원하는 모드는 **Q1·Q4**다. Q5·Q6은 아직 구현하지 않았다.

A와 B만으로는 AI 답변 경로가 없어, 연결을 위해 `models/chat.py`, `routers/chat.py`, `services/llm.py`와 `static/`의 간단한 화면도 추가했다. C·D 작업을 합칠 때 이 파일들과 API를 기준으로 조정한다.

### Codyssey API 설정

사진에 나온 `https://copa.codyssey.kr`의 OpenAI 호환 API를 사용한다. Claude Code 설정 파일은 이 FastAPI 프로그램에서 읽지 않는다. 프로젝트 루트 `.env`에 설정한다.

```dotenv
LLM_BASE_URL=https://copa.codyssey.kr/v1
LLM_API_KEY=발급받은_Codyssey_키
LLM_MODEL=gpt-5-mini
LLM_TIMEOUT_SECONDS=30
NAVER_CLIENT_ID=발급받은_네이버_Client_ID
NAVER_CLIENT_SECRET=발급받은_네이버_Client_Secret
NAVER_TIMEOUT_SECONDS=5
```

- Codyssey 키는 AI 답변 생성용이다. 네이버 뉴스·데이터랩 조회에는 별도의 네이버 키가 필요하다.
- `gpt-5-mini`는 연결 당시 `/v1/models` 응답에서 확인한 모델이다. 키의 허용 모델이 달라지면 `LLM_MODEL`을 수정한다.
- `.env`를 바꾼 뒤 **서버를 재시작**한다. 현재 설정은 서버 시작 때 읽는다.
- 키는 서버에서만 사용하며 HTML·JavaScript·로그에 넣지 않는다. `.env`는 Git에서 제외된다.
- 네이버 키가 없거나 조회에 실패하면 실시간 데이터를 지어내지 않고 데이터 부족을 알린다. AI와 일반적인 콘텐츠 기획 대화는 가능하다.
- AI 요청 형식: [OpenAI Chat Completions 공식 명세](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create). 실제 요청은 설정된 Codyssey 주소로 전송한다.

### 트렌드 판정의 범위

한국 시간으로 어제까지의 완료된 14일을 **한 요청**으로 조회한다. 최근 7일 평균이 이전 7일보다 20% 이상 높으면 `rising`, 20% 이상 낮으면 `falling`이다. 그 사이이며 최근 상대지수가 80 이상이면 `peak`(정점 후보), 나머지는 `stable`(보합)이다. 정점 후보는 휴리스틱이며 실제 정점을 확정하지 않는다.

빈 응답, 14일 데이터 누락, 전 기간 0이면 `unknown`, `available=false`, 평균은 `null`이다. 원래 계획서의 3개 상태 외에 보합·자료 부족을 구분하기 위해 `stable`과 `unknown`을 추가했다. 최신 뉴스 목록을 인기 순위나 전체 언급량으로 표시하지 않는다.

### 연결 API

| 메서드 | 경로 | 용도 |
|---|---|---|
| GET | `/api/me` | 로그인 사용자와 설정 여부 확인(키 값 제외) |
| POST | `/api/chat` | Q1·Q4 질문, AI 응답, 로그 저장 |
| GET | `/api/me/chats?limit=20` | 내 기록 조회, 최신순, 1~100개 |

```json
{"mode":"q4","message":"금리 인하 주제 지금 올려도 돼?","keyword":"금리 인하"}
```

`keyword`는 생략할 수 있다. 성공은 `{"chat_id":1,"answer":"..."}`이며, 비로그인 401, 입력 오류 422, AI 연결 오류 502, 시간 초과 504, 저장 오류 500을 반환한다.

### 검증

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
```

일반 테스트는 실제 AI·네이버 API를 호출하지 않는다. 실제 연결을 확인하려면 아래 명령을 별도로 실행한다. **실제 API 사용량이 발생할 수 있으며**, 임시 DB에서 가입·로그인·Q4 요청·기록 조회를 검사한다. 운영 `app.db`는 변경하지 않는다.

```bash
.venv/bin/python -m scripts.check_connection
```
