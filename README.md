# PULSE · 경제 숏폼 트렌드 챗봇

경제·AI 숏폼 제작자를 위한 FastAPI 챗봇입니다. 회원가입·로그인 후 네이버 뉴스·검색 추이를 참고하여 AI와 기획하고, 사용자별 대화 기록을 확인합니다.

## 현재 통합 상태

A의 인증·SQLite, B의 트렌드, 서버 AI 연결, D의 PULSE UI를 연결했습니다. 실제 앱은 `app.main:app`이며 다섯 모드 모두 서버 프롬프트·LLM·대화 저장 경로를 사용합니다. `dev.demo_app:app`은 외부 API를 호출하지 않는 별도의 고정 응답 데모입니다.

| 모드 | 기능 |
| --- | --- |
| Q1 | 오늘의 주제: 최신 경제 뉴스와 최근/이전 검색 추이, 추천 주제·내용 |
| Q2 | 운영 채널 추천: 과거 업로드 주제 확보 후 관련 자료와 연결 주제 추천 |
| Q3 | 타이밍 체크: 주제의 검색 관심도를 비교해 지금/기다리기/다른 각도 제안 |
| Q4 | 새로운 각도: 반전·비교·논쟁·정보·경험형의 5~10개 아이디어와 최종 추천 |
| Q5 | 다음 편 기획: 이전 주제에서 파생한 후보, 1→2→3편 구조와 오늘의 다음 편 |

뉴스는 최신순 일부 검색 결과이며 인기 순위나 전체 언급량이 아닙니다. 데이터가 없거나 조회에 실패하면 실시간 사실을 지어내지 않고 한계를 알리도록 프롬프트에 명시합니다. 실제 답변 품질과 키 권한은 별도 실서비스 확인이 필요합니다. 배포·외부 접속 설정은 포함하지 않습니다.

## 실행

Python 3.10 이상. 기존 가상환경과 `.env`가 있으면 그대로 사용하며, 예제 파일로 덮어쓰지 마세요.

macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# .env가 없을 때만 실행
cp -n .env.example .env
.venv/bin/python -c "import secrets; print(secrets.token_hex(32))"
# 생성한 값을 .env의 SECRET_KEY에 넣고 나머지 API 설정을 채운 뒤 실행
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Windows PowerShell에서는 `.venv/bin/python` 대신 `./.venv/Scripts/python.exe`를 사용합니다. `.env`가 없을 때만 `Copy-Item .env.example .env`로 복사합니다.

1. `http://127.0.0.1:8000/signup`에서 회원가입합니다.
2. `/login`에서 로그인합니다.
3. `/`에서 Q1~Q5 중 하나를 선택해 질문합니다. Q2는 과거 업로드 주제를 먼저 입력합니다.
4. `/history`에서 사용자별 성공·실패 기록을 확인합니다.

상태 확인: `/health`. API 문서: `/docs`. `.env`를 바꾸면 서버를 재시작합니다. 서버는 기본 `app.db`에 users·chats 테이블을 생성합니다.

## 환경 변수와 API 연결

| 변수 | 설명 / 기본값 |
| --- | --- |
| `SECRET_KEY` | 필수 세션 서명 키, 16자 이상 |
| `DATABASE_URL` | `sqlite:///./app.db` |
| `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` | 네이버 뉴스·데이터랩용 인증 쌍 |
| `NAVER_TIMEOUT_SECONDS` | 네이버 개별 요청 제한, 기본 5초 |
| `LLM_API_KEY` | Codyssey에서 발급한 AI 키 |
| `LLM_BASE_URL` | `https://copa.codyssey.kr/v1` |
| `LLM_MODEL` | `.env.example`은 `gpt-5-mini`, 사용 계정의 허용 모델 지정 |
| `LLM_TIMEOUT_SECONDS` | AI 호출 전체 제한, 기본 30초 |

사진의 Claude Code 설정 파일을 이 앱에서 읽지는 않습니다. 프로젝트 `.env`를 사용합니다. Codyssey 키로 네이버 API를 조회할 수는 없으며 두 인증은 별개입니다. AI 클라이언트는 [OpenAI Chat Completions 명세](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) 형식으로 설정된 게이트웨이에 요청합니다.

키는 서버에서만 사용합니다. `.env`·가상환경·DB는 Git에서 제외됩니다. 브라우저는 같은 출처의 `/api/*`만 호출합니다. D 페이지는 CSP와 `textContent`로 질문·답변의 HTML 실행을 방지합니다.

## 구조와 연결

```text
app/
├── main.py, config.py, database.py       # 기반·설정·DB
├── dependencies.py, errors.py, security.py
├── models/user.py, chat.py              # 사용자·대화
├── routers/auth.py, chat.py             # 인증·AI 요청
├── routers/pages.py, logs.py            # D 페이지·기록 조회
├── services/trend.py, llm.py            # 네이버·AI
├── services/scenarios/q1.py ~ q5.py      # 최신 UI 모드별 프롬프트
├── ui.py                               # 페이지·static·기록 라우터 등록
├── templates/                          # D Jinja2 템플릿
└── static/css/, static/js/              # D UI
```

`main.py`는 `auth.router`, `chat.router`를 등록하고 `install_ui(..., chat_model=models.Chat)`를 한 번 호출합니다. `/static`, `/`, `/api/me/chats`는 D 등록만 사용하여 중복 경로를 피합니다. 이전 임시 단일 HTML 화면은 제거했습니다.

사용자별 최근 **성공 대화 5개**를 AI에 전달합니다. 외부 동기 HTTP 호출은 스레드로 분리하며 전체 트렌드 준비 시간도 제한합니다. 요청 수신, AI 시작·성공/실패, DB 저장 성공/실패를 기록합니다. 질문·키·AI 서비스의 원본 오류 본문은 로그에 넣지 않습니다.

## API

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| POST | `/api/auth/signup` | 회원가입, 201 |
| POST | `/api/auth/login` | 로그인·세션 쿠키, 200 |
| POST | `/api/auth/logout` | 로그인 필요, 204 |
| GET | `/api/me` | 내 사용자 정보·설정 여부, 키 값 제외 |
| POST | `/api/chat` | 로그인 필요, q1~q5 질문·AI 응답·저장 |
| GET | `/api/me/chats?limit=20` | 내 기록만 최신순, 1~100개, no-store |

```json
{"mode":"q3","message":"금리 인하 주제 지금 올려도 돼?","keyword":"금리 인하"}
```

`keyword`는 API에서 선택적으로 지정할 수 있습니다. UI는 질문에서 키워드를 추출하는 기본 경로를 사용합니다. Q2 UI는 `최근 업로드 주제: ...\n질문: ...`를 한 message로 전송하며 전체 500자 제한을 적용합니다. API에서 맥락 없이 Q2를 호출하면 먼저 과거 업로드 주제를 물어보도록 지시합니다.

성공: `{"chat_id":1,"answer":"..."}`. 비로그인 401, 입력 오류 422, AI 실패 502, 시간 초과 504, 저장 오류 500입니다. 기록 조회 DB 실패는 D 라우터에서 503으로 처리합니다. 시간 초과·AI 오류도 answer=null로 저장합니다.

## 시나리오 번호와 기존 기록

현재 계약은 [docs/SCENARIOS.md](docs/SCENARIOS.md)의 Q1~Q5입니다. **이전 API의 q4 타이밍 호출은 q3로 바꾸세요.** 새 q4는 새로운 각도입니다.

`chats.scenario_version`으로 기록의 번호 체계를 구분합니다. 서버 시작 시 기존 chats 테이블에 해당 열이 없으면 기본 1로 추가하며, 원래 mode·질문·답변은 그대로 보존합니다. 새 기록은 버전 2입니다. 기록 API는 버전 1의 q4/q5/q6를 새 UI q3/q4/q5로 변환하여 응답합니다. API 응답 필드 수는 기존 계약과 같습니다. SQL에서 원본 mode를 볼 때는 scenario_version도 함께 확인하세요. 스키마 변경은 반복 실행해도 열을 중복 추가하지 않습니다.

users와 chats는 user_id로 연결됩니다. DB 생성 시각은 UTC이며 D 화면은 offset 없는 시각을 `(서버 시각)`으로 표시합니다.

## 트렌드 판정의 한계

한국 시간 어제까지 완료된 14일을 한 번에 조회하여 같은 척도로 비교합니다. 최근 7일 평균이 이전 7일보다 20% 이상 높으면 rising, 20% 이상 낮으면 falling입니다. 그 사이에서 상대지수가 80 이상이면 peak(정점 후보), 나머지는 stable(보합)입니다. 실제 정점을 확정하는 통계 모델은 아닙니다.

빈 응답·14일 데이터 누락·전 기간 0은 unknown, available=false, 평균 null입니다. 검색 상대지수는 조회수나 실제 검색 횟수가 아닙니다.

## 검증과 데모

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
```

테스트는 임시 DB와 모의 외부 응답을 사용하며 실제 유료 API를 호출하지 않습니다. 기존 인증·UI 테스트에 다섯 모드 분기·프롬프트·대화 저장·사용자 격리·오류·구 기록 호환 검사를 포함합니다.

실제 연결 확인은 아래 명령으로 별도 수행할 수 있습니다. **실제 API 사용량이 발생할 수 있습니다.** 임시 DB에서 가입→로그인→Q3 실제 AI 호출→기록을 확인하며 운영 app.db는 수정하지 않습니다.

```bash
.venv/bin/python -m scripts.check_connection
```

UI 전용 데모:

```bash
.venv/bin/python -m pip install -r requirements-ui-dev.txt
.venv/bin/python -m uvicorn dev.demo_app:app --host 127.0.0.1 --port 8001
```

데모 계정은 `demo@example.com` / `demo-pass-2026`입니다. 실제 계정이 아니며 예시 응답과 메모리 DB만 제공합니다. 데모 가입은 503, `[timeout]`·`[error]`는 데모 전용 실패 시뮬레이션입니다. 실제 앱 대신 데모를 운영하지 마세요.

브라우저 검사 도구: `requirements-ui-browser.txt`, `dev/check_ui_browser.py`, `dev/check_auth_browser.py`. 실행법과 D 작업 이력은 [D_HANDOFF.md](docs/D_HANDOFF.md)에 있습니다. 해당 문서의 통합 전 준비 중 상태는 이 README의 현재 상태와 구분합니다.

DB 읽기 전용 검사:

```bash
.venv/bin/python scripts/check_logs.py --db app.db --user-id 1 --limit 20
```

SQLite CLI 예시는 `scripts/check_logs.sql`을 참고하세요. 존재하지 않는 DB는 새로 만들지 않습니다.

## 역할과 협업

| 역할 | 브랜치 | 담당 |
| --- | --- | --- |
| A | feature/auth | 프로젝트 기반, User·세션 인증, 보안·검증 |
| B | feature/trend | 뉴스·검색 추이, 시나리오 데이터 |
| C | feature/chat | Chat·LLM·컨텍스트·분기·저장 |
| D | feature/ui | PULSE 화면·기록 조회·SQL·데모·문서 |

이번 feature/trend 통합에서는 A·B 연결에 필요했던 C 영역의 기본 구현을 최신 다섯 모드로 확장하고 D UI를 연결했습니다. 이후 C 브랜치와 합칠 때 Chat·LLM·채팅 라우터의 중복 구현을 확인하세요.

팀 정책은 feature/* → develop → main, PR 리뷰 후 merge commit입니다. 배포와 실제 API 데이터·응답 품질 검증은 별도이며, 로컬 테스트 성공만으로 완료 표시하지 않습니다.
